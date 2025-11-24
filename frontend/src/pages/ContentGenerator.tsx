import React, { useState, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { Sparkles, Twitter, Instagram, Linkedin, Facebook, Mail, Loader2, Copy, Check, Upload, X, Image, Video } from 'lucide-react';
import { promptsAPI } from '../services/api';
import toast from 'react-hot-toast';

interface GenerateForm {
  prompt: string;
}

interface GeneratedPost {
  id: number;
  platform: string;
  content: string;
  status: string;
}

interface GenerationResponse {
  prompt_id: number;
  generated_posts: GeneratedPost[];
}

const platforms = [
  { id: 'twitter', name: 'Twitter', icon: Twitter, color: 'text-blue-400' },
  { id: 'instagram', name: 'Instagram', icon: Instagram, color: 'text-pink-400' },
  { id: 'linkedin', name: 'LinkedIn', icon: Linkedin, color: 'text-blue-600' },
  { id: 'facebook', name: 'Facebook', icon: Facebook, color: 'text-blue-700' },
  { id: 'email', name: 'Email', icon: Mail, color: 'text-gray-600' },
];

const ContentGenerator: React.FC = () => {
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(['twitter', 'instagram', 'linkedin']);
  const [generatedContent, setGeneratedContent] = useState<GenerationResponse | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [copiedPlatform, setCopiedPlatform] = useState<string | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<GenerateForm>();

  const togglePlatform = (platformId: string) => {
    setSelectedPlatforms(prev =>
      prev.includes(platformId)
        ? prev.filter(p => p !== platformId)
        : [...prev, platformId]
    );
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    const validFiles = files.filter(file => {
      const fileType = file.type;
      const isValidImage = fileType.startsWith('image/') && ['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(fileType);
      const isValidVideo = fileType.startsWith('video/') && ['video/mp4', 'video/avi', 'video/mov', 'video/webm'].includes(fileType);
      const isValidSize = file.size <= 50 * 1024 * 1024; // 50MB limit
      
      if (!isValidImage && !isValidVideo) {
        toast.error(`Unsupported file type: ${file.name}`);
        return false;
      }
      if (!isValidSize) {
        toast.error(`File too large: ${file.name} (max 50MB)`);
        return false;
      }
      return true;
    });

    setUploadedFiles(prev => [...prev, ...validFiles]);
    if (validFiles.length > 0) {
      toast.success(`Added ${validFiles.length} file(s)`);
    }
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const getFileIcon = (file: File) => {
    return file.type.startsWith('image/') ? Image : Video;
  };

  const onSubmit = async (data: GenerateForm) => {
    if (selectedPlatforms.length === 0) {
      toast.error('Please select at least one platform');
      return;
    }

    setIsGenerating(true);
    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('prompt', data.prompt);
      formData.append('platforms', JSON.stringify(selectedPlatforms));
      
      // Add uploaded files
      uploadedFiles.forEach(file => {
        formData.append('files', file);
      });

      const response = await promptsAPI.generateContentWithFiles(formData);
      setGeneratedContent(response.data);
      toast.success('Content generated successfully!');
    } catch (error) {
      console.error('Content generation error:', error);
      toast.error('Failed to generate content');
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = async (content: string, platform: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedPlatform(platform);
      toast.success('Content copied to clipboard!');
      setTimeout(() => setCopiedPlatform(null), 2000);
    } catch (error) {
      toast.error('Failed to copy content');
    }
  };

  const regenerateContent = async () => {
    if (!generatedContent) return;

    setIsGenerating(true);
    try {
      const response = await promptsAPI.regenerateContent(
        generatedContent.prompt_id,
        selectedPlatforms
      );
      setGeneratedContent(response.data);
      toast.success('Content regenerated successfully!');
    } catch (error) {
      console.error('Content regeneration error:', error);
      toast.error('Failed to regenerate content');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Generate Content</h1>
        <p className="mt-1 text-sm text-gray-500">
          Create AI-powered content for multiple social media platforms from a single prompt
        </p>
      </div>

      {/* Generation Form */}
      <div className="card">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Prompt Input */}
          <div>
            <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-2">
              What would you like to create content about?
            </label>
            <textarea
              id="prompt"
              rows={4}
              {...register('prompt', {
                required: 'Please enter a prompt',
                minLength: {
                  value: 10,
                  message: 'Prompt must be at least 10 characters',
                },
              })}
              className={`input-field resize-none ${
                errors.prompt ? 'border-red-500' : ''
              }`}
              placeholder="e.g., Write a post about the benefits of AI in modern business..."
              disabled={isGenerating}
            />
            {errors.prompt && (
              <p className="mt-1 text-sm text-red-600">{errors.prompt.message}</p>
            )}
          </div>

          {/* File Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Upload images or videos (optional)
            </label>
            <div className="space-y-4">
              {/* Upload Button */}
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 cursor-pointer transition-colors"
              >
                <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-600">
                  Click to upload images or videos
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Supports JPG, PNG, GIF, WebP, MP4, AVI, MOV, WebM (max 50MB each)
                </p>
              </div>
              
              {/* Hidden File Input */}
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*,video/*"
                onChange={handleFileUpload}
                className="hidden"
              />
              
              {/* Uploaded Files */}
              {uploadedFiles.length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm font-medium text-gray-700">Uploaded files:</p>
                  <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                    {uploadedFiles.map((file, index) => {
                      const FileIcon = getFileIcon(file);
                      return (
                        <div key={index} className="flex items-center p-2 bg-gray-50 rounded-lg">
                          <FileIcon className="h-4 w-4 text-gray-500 mr-2" />
                          <span className="text-xs text-gray-700 truncate flex-1">
                            {file.name}
                          </span>
                          <button
                            type="button"
                            onClick={() => removeFile(index)}
                            className="ml-2 text-gray-400 hover:text-red-500"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Platform Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Select platforms to generate content for:
            </label>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
              {platforms.map((platform) => (
                <button
                  key={platform.id}
                  type="button"
                  onClick={() => togglePlatform(platform.id)}
                  className={`flex flex-col items-center p-4 rounded-lg border-2 transition-colors ${
                    selectedPlatforms.includes(platform.id)
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <platform.icon className={`h-6 w-6 ${platform.color} mb-2`} />
                  <span className="text-sm font-medium text-gray-700">{platform.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Generate Button */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={isGenerating || selectedPlatforms.length === 0}
              className="btn-primary flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 mr-2" />
                  Generate Content
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Generated Content */}
      {generatedContent && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-medium text-gray-900">Generated Content</h2>
            <button
              onClick={regenerateContent}
              disabled={isGenerating}
              className="btn-secondary flex items-center disabled:opacity-50"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Regenerating...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 mr-2" />
                  Regenerate
                </>
              )}
            </button>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {generatedContent.generated_posts.map((post) => {
              const platform = platforms.find(p => p.id === post.platform);
              return (
                <div key={post.id} className="card">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center">
                      {platform && (
                        <>
                          <platform.icon className={`h-5 w-5 ${platform.color} mr-2`} />
                          <span className="font-medium text-gray-900 capitalize">{platform.name}</span>
                        </>
                      )}
                    </div>
                    <button
                      onClick={() => copyToClipboard(post.content, post.platform)}
                      className="flex items-center text-sm text-gray-500 hover:text-gray-700"
                    >
                      {copiedPlatform === post.platform ? (
                        <>
                          <Check className="h-4 w-4 mr-1" />
                          Copied
                        </>
                      ) : (
                        <>
                          <Copy className="h-4 w-4 mr-1" />
                          Copy
                        </>
                      )}
                    </button>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-900 whitespace-pre-wrap">{post.content}</p>
                  </div>
                  <div className="mt-4 flex items-center justify-between">
                    <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                      post.status === 'draft' ? 'text-gray-600 bg-gray-100' : 'text-green-600 bg-green-100'
                    }`}>
                      {post.status}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentGenerator;
