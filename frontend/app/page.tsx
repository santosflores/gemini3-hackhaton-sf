"use client";

import { useState, useRef } from "react";
import { CopilotSidebar, useFrontendTool } from "@copilotkitnext/react";
import { z } from "zod";
import DebugPanel from "./components/DebugPanel";

interface UploadedVideo {
  name: string;
  size: string;
  url: string;
  image_paths?: string[];
}

export default function Home() {
  const [uploadedVideo, setUploadedVideo] = useState<UploadedVideo | null>(null);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Register Copilot Action to handle AI-driven state updates
  useFrontendTool({
    name: "set_play_visual_metadata",
    description: "Update the app state with generated play visualization images.",
    parameters: z.object({
      image_filenames: z.array(z.string()).describe("The filenames of the generated play visual images."),
      message: z.string().optional().describe("An optional message describing the update."),
    }),
    handler: async ({ image_filenames }) => {
      const imageUrls = image_filenames.map(filename => `http://localhost:8000/uploads/${filename}`);
      console.log("Receiving play visual metadata:", imageUrls);
      setUploadedVideo(prev => prev ? { ...prev, image_paths: imageUrls } : null);
      return `State updated with ${image_filenames.length} images.`;
    },
  });

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

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();

      setUploadedVideo({
        name: file.name,
        size: formatFileSize(file.size),
        url: `http://localhost:8000/uploads/${data.filename}`,
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

      <main className="flex min-h-screen w-full max-w-4xl flex-col items-center justify-between py-24 px-8 bg-white dark:bg-black sm:items-start">
        <CopilotSidebar
          defaultOpen={true}
          inputProps={{
            onAddFile: handleAddFile,
          }}
        />
        <div className="flex flex-col items-center gap-8 text-center sm:items-start sm:text-left w-full">
          <div className="space-y-2">
            <h1 className="text-5xl font-extrabold tracking-tight text-zinc-900 dark:text-white">The Defensive CoordAInator</h1>
            <p className="text-lg text-zinc-500">Analyze your football plays with precision.</p>
          </div>

          {!uploadedVideo && !uploading && (
            <div
              onClick={handleAddFile}
              className="group relative w-full aspect-video flex flex-col items-center justify-center border-2 border-dashed border-zinc-200 dark:border-zinc-800 rounded-2xl cursor-pointer hover:border-blue-500 dark:hover:border-blue-500 transition-all bg-zinc-50/50 dark:bg-zinc-900/50"
            >
              <div className="flex flex-col items-center gap-4 group-hover:scale-110 transition-transform">
                <div className="w-16 h-16 flex items-center justify-center bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-full">
                  <span className="text-3xl">📹</span>
                </div>
                <div className="space-y-1 text-center">
                  <p className="text-xl font-semibold">Upload Play Video</p>
                  <p className="text-sm text-zinc-500">Click to select an MP4 film</p>
                </div>
              </div>
            </div>
          )}

          {/* Upload Status / Video Player */}
          {(uploading || uploadedVideo) && (
            <div className="w-full space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
              {uploading ? (
                <div className="w-full aspect-video flex flex-col items-center justify-center bg-zinc-100 dark:bg-zinc-900 rounded-2xl">
                  <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                    <p className="text-zinc-500 font-medium tracking-wide">Processing film...</p>
                  </div>
                </div>
              ) : uploadedVideo && (
                <div className="group relative w-full overflow-hidden rounded-2xl bg-black shadow-2xl ring-1 ring-zinc-200 dark:ring-zinc-800">
                  <video
                    src={uploadedVideo.url}
                    controls
                    className="w-full aspect-video h-auto"
                  />
                  <div className="absolute top-4 left-4 p-3 bg-black/60 backdrop-blur-md rounded-xl text-white opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-3">
                    <span className="text-lg">🎬</span>
                    <div>
                      <p className="text-xs font-bold leading-none">{uploadedVideo.name}</p>
                      <p className="text-[10px] text-white/60 mt-1">{uploadedVideo.size}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Play Visual Display - Gallery */}
              {uploadedVideo && uploadedVideo.image_paths && uploadedVideo.image_paths.length > 0 && (
                <div className="space-y-6 animate-in fade-in zoom-in-95 duration-700 pt-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 flex items-center justify-center bg-blue-100 dark:bg-blue-900/30 rounded-xl">
                      <span className="text-xl">📊</span>
                    </div>
                    <h3 className="text-2xl font-bold text-zinc-900 dark:text-white tracking-tight">Tactical Playbook Diagrams</h3>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {uploadedVideo.image_paths.map((path, idx) => (
                      <div
                        key={idx}
                        className="group relative overflow-hidden rounded-2xl bg-white dark:bg-zinc-900 shadow-xl border border-zinc-200 dark:border-zinc-800 transition-all hover:shadow-2xl hover:scale-[1.02]"
                      >
                        <img
                          src={path}
                          alt={`Play Analysis Diagram ${idx + 1}`}
                          className="w-full h-auto object-cover"
                        />
                        <div className="absolute inset-0 bg-blue-600/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                        <div className="absolute bottom-4 left-4 right-4 p-2 bg-black/60 backdrop-blur-md rounded-lg text-white text-[10px] font-medium opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-between">
                          <span>Diagram {idx + 1}</span>
                          <a
                            href={path}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="bg-white/20 hover:bg-white/40 px-2 py-1 rounded transition-colors"
                          >
                            View Full
                          </a>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          <div className="flex items-center gap-4 w-full">
            <button
              onClick={handleAddFile}
              className="px-6 py-3 bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 font-bold rounded-xl hover:scale-105 active:scale-95 transition-all flex items-center gap-2 text-sm"
            >
              <span>📁</span> Choose Another
            </button>
            <div className="h-px flex-1 bg-zinc-100 dark:bg-zinc-800" />
          </div>
        </div>
      </main>

      {/* Floating Debug Panel - Left Side */}
      <div className="fixed bottom-4 left-4 w-[480px] z-50">
        <DebugPanel />
      </div>
    </div>
  );
}

