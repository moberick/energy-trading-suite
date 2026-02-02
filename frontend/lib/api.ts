const API_BASE_URL = "http://localhost:8000/api";

export async function fetchPositions() {
    const response = await fetch(`${API_BASE_URL}/trades/positions`);
    if (!response.ok) {
        throw new Error("Failed to fetch positions");
    }
    return response.json();
}

export async function fetchCurve() {
    const response = await fetch(`${API_BASE_URL}/curve`);
    if (!response.ok) {
        throw new Error("Failed to fetch curve");
    }
    return response.json();
}

export async function fetchPnLAttribution() {
    const response = await fetch(`${API_BASE_URL}/pnl/attribution`);
    if (!response.ok) {
        throw new Error("Failed to fetch PnL attribution");
    }
    return response.json();
}

export async function fetchArbOptimize(fobLocation: string = "USGC") {
    const response = await fetch(`${API_BASE_URL}/arb/optimize?fob_location=${fobLocation}`);
    if (!response.ok) {
        throw new Error("Failed to fetch Arb optimization");
    }
    return response.json();
}

export async function decomposePnL() {
    const response = await fetch(`${API_BASE_URL}/pnl/decompose`, { method: 'POST' });
    if (!response.ok) {
        throw new Error("Failed to decompose PnL");
    }
    return response.json();
}
