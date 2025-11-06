'use client'

import Link from 'next/link'
import { useState } from 'react'
import { Terminal, Github, MessageCircle, Zap, Code, Globe } from 'lucide-react'

export default function AboutPage() {
  const [demoMode, setDemoMode] = useState<'CLI' | 'UI'>('CLI')
  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <Terminal className="w-16 h-16 text-accent mx-auto mb-6" />
          <h1 className="text-5xl font-heading font-bold mb-6">
             <span className="text-gradient">About ParagonAI</span>
          </h1>
          <p className="text-xl text-text/70 max-w-2xl mx-auto">
            Empowering developers to deploy GenAI agents from prompt to production with speed, 
            reliability, and intuitive tooling.
          </p>
        </div>

        {/* CLI + Backend Flow */}
        <div className="card mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-3xl font-heading font-bold">How It Works</h2>
            {/* Segmented toggle: larger, animated thumb */}
            <div
              className="relative flex items-center w-56 h-12 rounded-full border border-[#1F1F1F] bg-[#0B0B0B] overflow-hidden"
              role="tablist"
              aria-label="Demo mode"
            >
              <div
                className={`absolute top-0 left-0 h-full w-1/2 transition-transform duration-300 ease-out ${demoMode === 'CLI' ? 'translate-x-0' : 'translate-x-full'}`}
                style={{ background: 'var(--accent, #606060)' }}
                aria-hidden="true"
              />
              <button
                role="tab"
                aria-selected={demoMode === 'CLI'}
                className={`relative z-10 flex-1 h-full inline-flex items-center justify-center gap-2 px-4 text-sm sm:text-base font-semibold ${demoMode === 'CLI' ? 'text-black' : 'text-text/80 hover:text-accent'}`}
                onClick={() => setDemoMode('CLI')}
              >
                <Terminal className="w-5 h-5" />
                CLI
              </button>
              <button
                role="tab"
                aria-selected={demoMode === 'UI'}
                className={`relative z-10 flex-1 h-full inline-flex items-center justify-center gap-2 px-4 text-sm sm:text-base font-semibold ${demoMode === 'UI' ? 'text-black' : 'text-text/80 hover:text-accent'}`}
                onClick={() => setDemoMode('UI')}
              >
                <Globe className="w-5 h-5" />
                UI
              </button>
            </div>
          </div>
          <div className="rounded-lg overflow-hidden border border-[#1F1F1F] bg-black p-2">
            <img
              src={demoMode === 'CLI' ? '/assets/cli_demo.gif' : '/assets/web_demo.gif'}
              alt={demoMode === 'CLI' ? 'CLI demo' : 'Web demo'}
              className="w-full h-auto rounded"
            />
          </div>
        </div>

        {/* Purpose Section */}
        <div className="card mb-8">
          <h2 className="text-3xl font-heading font-bold mb-4">Our Purpose</h2>
          <p className="text-text/80 mb-4 leading-relaxed">
            ParagonAI bridges the gap between AI experimentation and production deployment. 
            We believe that deploying AI agents should be as simple as writing a prompt. 
            Our platform combines the power of command-line tools with a comprehensive dashboard 
            to give developers full control over their GenAI agent lifecycle.
          </p>
          <p className="text-text/80 leading-relaxed">
            Whether you're building conversational agents, API services, or data processing pipelines, 
            ParagonAI provides the infrastructure and monitoring tools you need to ship with confidence.
          </p>
        </div>

        {/* Community Section */}
        <div className="card text-center">
          <h2 className="text-3xl font-heading font-bold mb-4">About the Idea</h2>
          <p className="text-text/70 mb-6">
            This project was built in 24 hours at <span className="font-semibold">Canada's GenAI DevOps Hackathon 2025</span> by <span className="font-semibold">The Null Pointers</span>.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center text-left">
            {[
              { name: 'Siddharth Lamba', github: 'https://github.com/lambasid', linkedin: 'https://www.linkedin.com/in/sid-lamba/' },
              { name: 'Aman Purohit', github: 'https://github.com/purohitamann', linkedin: 'https://www.linkedin.com/in/amanhiranpurohit/' },
              { name: 'George Farag', github: 'https://github.com/georgef166', linkedin: 'https://www.linkedin.com/in/gfarag/' },
              { name: 'Hassan Elbaytam', github: 'https://github.com/HMBaytam', linkedin: 'https://www.linkedin.com/in/hmbaytam/' },
              { name: 'Minh Pham', github: 'https://github.com/phamduyanminh', linkedin: 'https://www.linkedin.com/in/minhp3120/' }
            ].map((member) => (
              <div
                key={member.github}
                className="flex items-center gap-3 bg-[#0B0B0B] border border-[#1F1F1F] rounded-md px-4 py-2"
              >
                <span className="font-semibold">{member.name}</span>

                <a
                  href={member.github}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={`GitHub — ${member.name}`}
                  className="text-text/80 hover:text-accent"
                >
                  <Github className="w-5 h-5" />
                </a>

                <a
                  href={member.linkedin}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={`LinkedIn — ${member.name}`}
                  className="text-text/80 hover:text-accent"
                >
                  {/* simple LinkedIn SVG */}
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                    <path d="M4.98 3.5C4.98 4.88 3.86 6 2.48 6S0 4.88 0 3.5 1.12 1 2.5 1 4.98 2.12 4.98 3.5zM.5 8h3.96V24H.5zM8.5 8h3.8v2.18h.05c.53-1 1.83-2.18 3.77-2.18 4.03 0 4.77 2.65 4.77 6.09V24h-3.96v-7.1c0-1.7-.03-3.9-2.38-3.9-2.38 0-2.74 1.86-2.74 3.78V24H8.5V8z" />
                  </svg>
                </a>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

