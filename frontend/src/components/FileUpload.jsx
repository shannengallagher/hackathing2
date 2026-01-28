import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { uploadSyllabus, getUploadStatus } from '../services/api'

export default function FileUpload({ onUploadComplete }) {
  const [uploadState, setUploadState] = useState('idle') // idle, uploading, processing, complete, error
  const [error, setError] = useState(null)
  const [processingStatus, setProcessingStatus] = useState(null)
  const queryClient = useQueryClient()

  const uploadMutation = useMutation({
    mutationFn: uploadSyllabus,
    onSuccess: async (data) => {
      setUploadState('processing')
      // Poll for completion
      const pollStatus = async () => {
        try {
          const status = await getUploadStatus(data.id)
          setProcessingStatus(status)

          if (status.status === 'completed') {
            setUploadState('complete')
            // Invalidate and refetch all related queries
            await Promise.all([
              queryClient.invalidateQueries({ queryKey: ['assignments'] }),
              queryClient.invalidateQueries({ queryKey: ['syllabi'] }),
            ])
            // Force immediate refetch
            await Promise.all([
              queryClient.refetchQueries({ queryKey: ['assignments'] }),
              queryClient.refetchQueries({ queryKey: ['syllabi'] }),
            ])
            if (onUploadComplete) onUploadComplete(data.id)
          } else if (status.status.startsWith('failed')) {
            setUploadState('error')
            setError(status.status)
          } else {
            setTimeout(pollStatus, 1000)
          }
        } catch (err) {
          setUploadState('error')
          setError('Failed to check processing status')
        }
      }
      pollStatus()
    },
    onError: (err) => {
      setUploadState('error')
      setError(err.response?.data?.detail || 'Upload failed')
    },
  })

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      setUploadState('uploading')
      setError(null)
      uploadMutation.mutate(acceptedFiles[0])
    }
  }, [uploadMutation])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
  })

  const resetUpload = () => {
    setUploadState('idle')
    setError(null)
    setProcessingStatus(null)
  }

  if (uploadState === 'complete') {
    return (
      <div className="border-2 border-green-300 border-dashed rounded-lg p-8 text-center bg-green-50">
        <CheckCircle className="mx-auto h-12 w-12 text-green-500" />
        <h3 className="mt-4 text-lg font-medium text-green-900">Upload Complete!</h3>
        <p className="mt-2 text-sm text-green-600">
          Found {processingStatus?.assignment_count || 0} assignments
          {processingStatus?.course_name && ` in ${processingStatus.course_name}`}
        </p>
        <button
          onClick={resetUpload}
          className="mt-4 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
        >
          Upload Another
        </button>
      </div>
    )
  }

  if (uploadState === 'error') {
    return (
      <div className="border-2 border-red-300 border-dashed rounded-lg p-8 text-center bg-red-50">
        <AlertCircle className="mx-auto h-12 w-12 text-red-500" />
        <h3 className="mt-4 text-lg font-medium text-red-900">Upload Failed</h3>
        <p className="mt-2 text-sm text-red-600">{error}</p>
        <button
          onClick={resetUpload}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
        >
          Try Again
        </button>
      </div>
    )
  }

  if (uploadState === 'uploading' || uploadState === 'processing') {
    return (
      <div className="border-2 border-blue-300 border-dashed rounded-lg p-8 text-center bg-blue-50">
        <Loader2 className="mx-auto h-12 w-12 text-blue-500 animate-spin" />
        <h3 className="mt-4 text-lg font-medium text-blue-900">
          {uploadState === 'uploading' ? 'Uploading...' : 'Processing with AI...'}
        </h3>
        <p className="mt-2 text-sm text-blue-600">
          {uploadState === 'processing'
            ? 'Extracting assignments and due dates'
            : 'Please wait'}
        </p>
      </div>
    )
  }

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
        isDragActive
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-300 hover:border-gray-400 bg-white'
      }`}
    >
      <input {...getInputProps()} />
      <Upload className="mx-auto h-12 w-12 text-gray-400" />
      <h3 className="mt-4 text-lg font-medium text-gray-900">Upload Syllabus</h3>
      <p className="mt-2 text-sm text-gray-500">
        {isDragActive
          ? 'Drop the file here'
          : 'Drag and drop a file, or click to select'}
      </p>
      <p className="mt-1 text-xs text-gray-400">
        PDF, Word (.docx), or Text files up to 10MB
      </p>
    </div>
  )
}
