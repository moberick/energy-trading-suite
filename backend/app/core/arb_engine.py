from typing import Dict, List, Optional, Any
import math

class OilArbCalculator:
    def __init__(self, volume_bbl: float = 700000):
        """
        Initialize with standard Aframax/Suezmax volume.
        Default 700k bbls (Aframax).
        """
        self.volume = volume_bbl

    def calculate_economics(
        self, 
        wti_price: float,
        brent_price: float,
        freight_rate_flat: float, # Flat rate in $/MT
        ws_points: float, # Worldscale points (e.g. 100 = 100% of flat rate)
        insurance_rate: float = 0.001,
        inspection_cost: float = 5000.0,
        demurrage_days: float = 0.0,
        demurrage_rate: float = 35000.0, # $/day
        loss_factor: float = 0.002 # 0.2% ocean loss
    ) -> Dict[str, float]:
        """
        Calculate Trans-Atlantic Arbitrage (WTI vs Brent).
        
        Economics = (Brent_DES - WTI_FOB) - Costs
        
        Where:
        - WTI_FOB: Price of WTI at USGC
        - Brent_DES: Price of Brent delivered to Europe (proxy)
        
        Actually, usually Arb is:
        Margin = (Brent Price - Freight - Costs) - WTI Price
        Or if moving WTI to Europe:
        Margin = (Brent_Linked_Sales_Price - Freight - Costs) - WTI_Purchase_Price
        """
        
        # 1. Freight Cost
        # Freight ($/MT) = Flat Rate * (WS / 100)
        freight_per_mt = freight_rate_flat * (ws_points / 100.0)
        
        # Convert to $/bbl (Approx 7.45 bbl/MT for light sweet crude)
        bbl_per_mt = 7.45 
        freight_per_bbl = freight_per_mt / bbl_per_mt
        
        total_freight_cost = freight_per_bbl * self.volume
        
        # 2. Other Costs
        insurance_cost = wti_price * self.volume * insurance_rate
        demurrage_cost = demurrage_days * demurrage_rate
        loss_cost = wti_price * self.volume * loss_factor
        
        total_variable_costs = insurance_cost + inspection_cost + demurrage_cost + loss_cost
        variable_cost_per_bbl = total_variable_costs / self.volume
        
        total_cost_per_bbl = freight_per_bbl + variable_cost_per_bbl
        
        # 3. Arb Margin
        # Assuming we buy WTI at USGC and sell as Brent-equivalent in Europe
        # Spread = Brent - WTI
        gross_spread = brent_price - wti_price
        
        net_margin_per_bbl = gross_spread - total_cost_per_bbl
        total_profit = net_margin_per_bbl * self.volume
        
        return {
            "wti_price": wti_price,
            "brent_price": brent_price,
            "gross_spread": round(gross_spread, 3),
            "freight_per_bbl": round(freight_per_bbl, 3),
            "variable_cost_per_bbl": round(variable_cost_per_bbl, 3),
            "total_cost_per_bbl": round(total_cost_per_bbl, 3),
            "net_margin_per_bbl": round(net_margin_per_bbl, 3),
            "total_profit": round(total_profit, 2),
            "is_open": net_margin_per_bbl > 0
        }

    def optimize_logistics(
        self,
        routes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare multiple freight options or routes.
        routes = [
            {"name": "Aframax USGC-Rotterdam", "ws": 110, "flat": 25.50, "volume": 700000},
            {"name": "Suezmax USGC-Rotterdam", "ws": 85, "flat": 25.50, "volume": 1000000}
        ]
        """
        best_margin = -float('inf')
        best_option = None
        results = []
        
        # Base prices for comparison (fixed for logistics optimization)
        # In real app, these might come from live curves
        wti_base = 75.00
        brent_base = 78.50
        
        for route in routes:
            # Create temp calculator for this volume
            calc = OilArbCalculator(volume_bbl=route.get('volume', self.volume))
            
            res = calc.calculate_economics(
                wti_price=wti_base,
                brent_price=brent_base,
                freight_rate_flat=route['flat'],
                ws_points=route['ws']
            )
            
            res['route_name'] = route['name']
            results.append(res)
            
        return {
            "best_route": best_option,
            "max_margin": best_margin,
            "all_scenarios": results
        }

class LNGCargo:
    def __init__(self, volume_mmbtu: float = 3800000):

        """
        Standard LNG Cargo (approx 174k m3 -> ~3.8M MMBtu)
        """
        self.volume = volume_mmbtu
        self.boil_off_daily = 0.0015 # 0.15% per day
        self.shipping_cost_daily = 100000 # $100k/day charter

    def optimize_route(
        self,
        fob_origin: str,
        destinations: Dict[str, Dict[str, float]] 
    ) -> Dict[str, Any]:
        """
        Calculate Netbacks for various destinations.
        destinations = {
            "JKM": {"price": 14.50, "distance": 9500},
            ...
        }
        """
        speed_knots = 17.0
        results = []
        best_netback = -float('inf')
        best_dest = None

        for dest_name, marketing_info in destinations.items():
            price_des = marketing_info['price']
            distance = marketing_info['distance']
            
            # Voyage Time (Days) = Distance / (Speed * 24)
            # Round trip or single leg? Usually netback considers single leg shipping cost to getting it there.
            # But charter is usually round trip. Let's assume single leg days * 2 for charter cost allocation?
            # Or simplified: Time = Distance / (17 * 24) * 1.15 (buffer)
            days_one_way = distance / (speed_knots * 24)
            days_round_trip = days_one_way * 2
            
            # Costs
            shipping_cost = days_round_trip * self.shipping_cost_daily
            shipping_cost_per_mmbtu = shipping_cost / self.volume
            
            # Boil off (Volume loss)
            # Loss = Volume * (1 - (1-boil_off)^days)
            # Simplified: Volume * boil_off * days
            boil_off_loss_volume = self.volume * self.boil_off_daily * days_one_way
            boil_off_cost = boil_off_loss_volume * price_des # Opportunity cost of lost cargo
            boil_off_per_mmbtu = boil_off_cost / self.volume
            
            total_shipping_per_mmbtu = shipping_cost_per_mmbtu + boil_off_per_mmbtu
            
            netback = price_des - total_shipping_per_mmbtu
            
            res = {
                "destination": dest_name,
                "market_price": price_des,
                "days_one_way": round(days_one_way, 1),
                "shipping_cost_per_mmbtu": round(shipping_cost_per_mmbtu, 3),
                "netback": round(netback, 3)
            }
            results.append(res)
            
            if netback > best_netback:
                best_netback = netback
                best_dest = dest_name
                
        return {
            "origin": fob_origin,
            "best_destination": best_dest,
            "max_netback": round(best_netback, 3),
            "all_routes": results
        }
