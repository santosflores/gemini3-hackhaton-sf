"use client";

import { CopilotSidebar } from "@copilotkitnext/react";

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-between py-32 px-16 bg-white dark:bg-black sm:items-start">
        <CopilotSidebar
          defaultOpen={true}
        />
        <div className="flex flex-col items-center gap-6 text-center sm:items-start sm:text-left">
          <h1 className="text-4xl font-bold">Agent Surface</h1>
          <p>Interact with the agent using the sidebar.</p>
        </div>
      </main>
    </div>
  );
}
