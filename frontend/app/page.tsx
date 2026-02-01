"use client";

import { useState, useRef } from "react";
import { CopilotSidebar } from "@copilotkitnext/react";
import DebugPanel from "./components/DebugPanel";

interface UploadedVideo {
  name: string;
  size: string;
}

export default function Home() {
  const [uploadedVideo, setUploadedVideo] = useState<UploadedVideo | null>(null);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const handleAddFile = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadedVideo({
      name: file.name,
      size: formatFileSize(file.size),
    });

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
    } catch (error) {
      console.error("Upload failed:", error);
    } finally {
      setUploading(false);
    }

    // Reset input
    e.target.value = "";
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="video/mp4"
        onChange={handleFileChange}
        className="hidden"
      />

      <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-between py-32 px-16 bg-white dark:bg-black sm:items-start">
        <CopilotSidebar
          defaultOpen={true}
          inputProps={{
            onAddFile: handleAddFile,
          }}
        />
        <div className="flex flex-col items-center gap-6 text-center sm:items-start sm:text-left w-full">
          <h1 className="text-4xl font-bold">Agent Surface</h1>
          <p>Interact with the agent using the sidebar.</p>

          {/* Upload Button */}
          <button
            onClick={handleAddFile}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
          >
            <span>📹</span> Upload MP4 Video
          </button>

          {/* Upload Status */}
          {(uploading || uploadedVideo) && (
            <div className="w-full p-4 bg-zinc-100 dark:bg-zinc-900 rounded-lg">
              {uploading ? (
                <p className="text-zinc-500">Uploading...</p>
              ) : uploadedVideo && (
                <>
                  <p className="font-medium">📹 {uploadedVideo.name}</p>
                  <p className="text-sm text-zinc-500">{uploadedVideo.size}</p>
                </>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Floating Debug Panel - Left Side */}
      <div className="fixed bottom-4 left-4 w-[480px] z-50">
        <DebugPanel />
      </div>
    </div>
  );
}

