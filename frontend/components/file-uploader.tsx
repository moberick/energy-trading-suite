"use client"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Upload, FileText, X } from "lucide-react"

interface FileUploaderProps {
  onUpload: (file: File) => void
  isLoading: boolean
}

export function FileUploader({ onUpload, isLoading }: FileUploaderProps) {
  const [file, setFile] = useState<File | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0])
    }
  }

  const handleSubmit = () => {
    if (file) {
      onUpload(file)
    }
  }

  const clearFile = () => {
    setFile(null)
    if (inputRef.current) {
      inputRef.current.value = ""
    }
  }

  return (
    <div className="w-full max-w-md mx-auto">
      {!file ? (
        <div
          className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors cursor-pointer"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          <Upload className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-2 text-sm text-gray-600">
            Drag & drop a CSV file here, or click to select
          </p>
          <Input
            ref={inputRef}
            type="file"
            accept=".csv"
            className="hidden"
            onChange={handleFileChange}
          />
        </div>
      ) : (
        <div className="bg-white border rounded-lg p-4 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-100 p-2 rounded">
                <FileText className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">{file.name}</p>
                <p className="text-xs text-gray-500">
                  {(file.size / 1024).toFixed(2)} KB
                </p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={clearFile}
              disabled={isLoading}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          <Button
            className="w-full bg-blue-600 hover:bg-blue-700"
            onClick={handleSubmit}
            disabled={isLoading}
          >
            {isLoading ? "Processing..." : "Upload & Analyze"}
          </Button>
        </div>
      )}
    </div>
  )
}
