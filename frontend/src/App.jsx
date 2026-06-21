import { useState, useRef, useEffect } from 'react'
import { UploadCloud, CheckCircle2, Loader2, PlayCircle, Link as LinkIcon, RefreshCw, XCircle } from 'lucide-react'

const API_BASE_URL = (typeof process !== 'undefined' && process.env && process.env.REACT_APP_API_URL) || import.meta.env.VITE_API_URL || "https://noct-creative-dispatch.onrender.com"

export default function App() {
  const [demoMode, setDemoMode] = useState(true)
  
  // Card 1: Asset Assembly
  const [productImage, setProductImage] = useState(null)
  const [styleVideo, setStyleVideo] = useState(null)
  const [rawIntent, setRawIntent] = useState('')
  const [isCompiling, setIsCompiling] = useState(false)
  
  // Card 2: Boxed Prompt Workspace
  const [compiledPrompt, setCompiledPrompt] = useState('')
  
  // Card 3: Video Generation Engine
  const tiers = [
    "Tier 1: Decent Videos ($0.03)",
    "Tier 2: Special Product Movements & Hyper-Realism ($0.12)",
    "Tier 3: Precision Cinematic Shots ($0.25)"
  ]
  const [selectedTier, setSelectedTier] = useState(tiers[1])
  
  // Card 4: Production Archive & Delivery
  const [isExecuting, setIsExecuting] = useState(false)
  const [statusEvents, setStatusEvents] = useState([])
  const [webViewLink, setWebViewLink] = useState('')
  const [hasError, setHasError] = useState(false)

  // Handlers
  const handleCompilePrompt = async () => {
    if (!productImage || !styleVideo || !rawIntent) {
      alert('Please provide Product Image, Style Video, and Raw Intent.')
      return
    }
    
    setIsCompiling(true)
    const formData = new FormData()
    formData.append('product_image', productImage)
    formData.append('style_video', styleVideo)
    formData.append('raw_intent', rawIntent)

    try {
      const response = await fetch(`${API_BASE_URL}/api/compile-prompt`, {
        method: 'POST',
        body: formData
      })
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Compilation Failed')
      }
      const data = await response.json()
      setCompiledPrompt(data.compiled_prompt)
    } catch (err) {
      alert(err.message)
    } finally {
      setIsCompiling(false)
    }
  }

  const handleExecutePipeline = () => {
    if (!compiledPrompt) {
      alert('Compile or enter a prompt first!')
      return
    }

    setIsExecuting(true)
    setStatusEvents([])
    setWebViewLink('')
    setHasError(false)

    // Build query params
    const params = new URLSearchParams({
      demo_mode: demoMode,
      compiled_prompt: compiledPrompt,
      selected_tier: selectedTier,
      product_image_name: productImage ? productImage.name : "demo_generated.png"
    })

    const evtSource = new EventSource(`${API_BASE_URL}/api/stream-generation?${params.toString()}`)
    
    evtSource.onmessage = (e) => {
      const data = JSON.parse(e.data)
      
      if (data.error) {
        setHasError(true)
        setStatusEvents(prev => [...prev.map(evt => ({...evt, type: evt.type === 'pending' ? 'error' : evt.type})), { status: data.error, type: 'error' }])
        evtSource.close()
        setIsExecuting(false)
        return
      }

      if (data.done) {
        setStatusEvents(prev => [...prev.map(evt => ({...evt, type: 'success'})), { status: `Executed: ${data.status}`, type: 'success' }])
        
        // Extract webViewLink from metadata
        if (data.metadata && data.metadata.length > 0) {
          setWebViewLink(data.metadata[0].webViewLink || '')
        }
        
        evtSource.close()
        setIsExecuting(false)
      } else {
        setStatusEvents(prev => [...prev.map(evt => ({...evt, type: 'success'})), { status: data.status, type: 'pending' }])
      }
    }

    evtSource.onerror = () => {
      setHasError(true)
      setStatusEvents(prev => [...prev, { status: 'Connection to engine lost.', type: 'error' }])
      evtSource.close()
      setIsExecuting(false)
    }
  }

  const getDemoVideoSrc = () => {
    if (!productImage) return "/demo.mp4";
    const baseName = productImage.name.split('.')[0];
    const baseNameUs = baseName.replace(/ /g, "_");
    
    let tierNum = 1;
    if (selectedTier.includes("Tier 2")) tierNum = 2;
    if (selectedTier.includes("Tier 3")) tierNum = 3;

    const availableVideos = [
      "Acne_heal_cream_tier1.mp4",
      "Acne_heal_cream_tier3.mp4",
      "Kumkumadi_face_cream.mp4",
      "Radiating_face_cream_tier3.mp4",
      "radiating_face_cream_tier2.mp4"
    ];

    const candidates = [];
    for (let t = tierNum; t <= 3; t++) {
      candidates.push(`${baseName}_tier${t}.mp4`);
      candidates.push(`${baseNameUs}_tier${t}.mp4`);
    }
    candidates.push(`${baseName}.mp4`);
    candidates.push(`${baseNameUs}.mp4`);

    for (const cand of candidates) {
      const found = availableVideos.find(v => v.toLowerCase() === cand.toLowerCase());
      if (found) return `/${found}`;
    }
    
    return `/${availableVideos[0]}`; // Fallback
  };

  const videoSrc = !demoMode ? webViewLink : (webViewLink ? getDemoVideoSrc() : "");

  return (
    <div className="flex flex-col h-screen w-screen bg-neutral-950 text-neutral-400 overflow-hidden font-sans">
      
      {/* Fixed Top Navbar */}
      <nav className="h-16 shrink-0 border-b border-neutral-800 bg-neutral-950 flex items-center justify-between px-8 z-50 shadow-sm">
        <div className="flex items-center space-x-3">
          <PlayCircle className="text-white w-6 h-6" />
          <h1 className="text-white font-semibold tracking-wide">NOCT CREATIVE DISPATCH</h1>
        </div>
        <div className="flex items-center space-x-6">
          <label className="flex items-center space-x-3 cursor-pointer">
            <span className="text-sm font-medium text-neutral-300">Demo Mode</span>
            <div className="relative">
              <input 
                type="checkbox" 
                className="sr-only" 
                checked={demoMode} 
                onChange={(e) => setDemoMode(e.target.checked)} 
              />
              <div className={`block w-10 h-6 rounded-full transition-colors ${demoMode ? 'bg-neutral-600' : 'bg-neutral-800'}`}></div>
              <div className={`dot absolute left-1 top-1 bg-white w-4 h-4 rounded-full transition-transform ${demoMode ? 'transform translate-x-4' : ''}`}></div>
            </div>
          </label>
        </div>
      </nav>

      {/* Horizontal Stepper Workspace */}
      <main className="flex-1 flex flex-row overflow-x-auto snap-x gap-16 p-10 px-16 custom-scrollbar items-stretch pb-12">
        
        {/* CARD 1: Asset Assembly */}
        <div className="snap-center shrink-0 min-w-[500px] w-[45vw] bg-neutral-900/40 border border-neutral-800 rounded-2xl flex flex-col p-8 shadow-xl">
          <h2 className="text-white font-medium mb-4 flex items-center space-x-2">
            <span className="bg-neutral-800 text-xs px-2 py-1 rounded-full text-neutral-300">Step 1</span>
            <span>Asset Assembly</span>
          </h2>
          <hr className="border-neutral-800 mb-6" />
          
          <div className="flex-1 flex flex-col space-y-5 overflow-y-auto custom-scrollbar pr-2">
            <div>
              <label className="block text-xs font-medium text-neutral-500 uppercase tracking-wider mb-2">Product Image (PNG)</label>
              <div className="border border-dashed border-neutral-700 bg-neutral-900 rounded-lg p-4 hover:border-neutral-500 transition-colors cursor-pointer relative group flex items-center justify-center h-24">
                <input type="file" accept="image/png" className="absolute inset-0 opacity-0 cursor-pointer" onChange={(e) => setProductImage(e.target.files[0])} />
                <div className="text-center">
                  {productImage ? <span className="text-white text-sm">{productImage.name}</span> : <div className="flex flex-col items-center"><UploadCloud className="w-5 h-5 text-neutral-500 mb-1" /><span className="text-xs text-neutral-500">Drop PNG here</span></div>}
                </div>
              </div>
            </div>
            
            <div>
              <label className="block text-xs font-medium text-neutral-500 uppercase tracking-wider mb-2">Style Reference (MP4)</label>
              <div className="border border-dashed border-neutral-700 bg-neutral-900 rounded-lg p-4 hover:border-neutral-500 transition-colors cursor-pointer relative group flex items-center justify-center h-24">
                <input type="file" accept="video/mp4" className="absolute inset-0 opacity-0 cursor-pointer" onChange={(e) => setStyleVideo(e.target.files[0])} />
                <div className="text-center">
                  {styleVideo ? <span className="text-white text-sm">{styleVideo.name}</span> : <div className="flex flex-col items-center"><UploadCloud className="w-5 h-5 text-neutral-500 mb-1" /><span className="text-xs text-neutral-500">Drop MP4 here</span></div>}
                </div>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-neutral-500 uppercase tracking-wider mb-2">Raw Design Intent</label>
              <input 
                type="text" 
                className="w-full bg-neutral-950 border border-neutral-800 rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:border-neutral-600 transition-colors"
                placeholder="e.g. Tamarind pods blooming..."
                value={rawIntent}
                onChange={(e) => setRawIntent(e.target.value)}
              />
            </div>
          </div>

          <div className="pt-6 mt-auto border-t border-neutral-800/50">
            <button 
              onClick={handleCompilePrompt}
              disabled={isCompiling}
              className="w-full bg-neutral-100 hover:bg-white text-neutral-900 font-semibold py-3 px-4 rounded-lg flex items-center justify-center space-x-2 transition-colors disabled:opacity-50"
            >
              {isCompiling ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
              <span>{isCompiling ? 'Compiling...' : 'Compile VLM Prompt'}</span>
            </button>
          </div>
        </div>

        {/* CARD 2: Boxed Prompt Workspace */}
        <div className="snap-center shrink-0 min-w-[500px] w-[45vw] bg-neutral-900/40 border border-neutral-800 rounded-2xl flex flex-col p-8 shadow-xl">
          <h2 className="text-white font-medium mb-4 flex items-center space-x-2">
            <span className="bg-neutral-800 text-xs px-2 py-1 rounded-full text-neutral-300">Step 2</span>
            <span>Boxed Prompt Workspace</span>
          </h2>
          <hr className="border-neutral-800 mb-6" />
          
          <div className="flex-1 flex flex-col min-h-0">
            <textarea 
              className="flex-1 w-full bg-[#050505] border-2 border-neutral-700 focus:border-neutral-500 rounded-xl p-5 text-[#a3e635] font-mono text-sm leading-relaxed resize-none custom-scrollbar outline-none transition-colors"
              value={compiledPrompt}
              onChange={(e) => setCompiledPrompt(e.target.value)}
              placeholder="Compiled prompt will appear here and is fully editable..."
            ></textarea>
          </div>
        </div>

        {/* CARD 3: Video Generation Engine */}
        <div className="snap-center shrink-0 min-w-[500px] w-[45vw] bg-neutral-900/40 border border-neutral-800 rounded-2xl flex flex-col p-8 shadow-xl">
          <h2 className="text-white font-medium mb-4 flex items-center space-x-2">
            <span className="bg-neutral-800 text-xs px-2 py-1 rounded-full text-neutral-300">Step 3</span>
            <span>Generation Engine</span>
          </h2>
          <hr className="border-neutral-800 mb-6" />
          
          <div className="flex flex-col space-y-4">
            {tiers.map((t, idx) => (
              <label key={idx} className={`flex items-start space-x-4 p-4 rounded-xl cursor-pointer border transition-colors ${selectedTier === t ? 'border-neutral-400 bg-neutral-800/50' : 'border-neutral-800 hover:border-neutral-700 bg-neutral-900/30'}`}>
                <div className="flex items-center h-5 mt-0.5">
                  <input 
                    type="radio" 
                    name="tier" 
                    value={t} 
                    checked={selectedTier === t} 
                    onChange={(e) => setSelectedTier(e.target.value)}
                    className="w-4 h-4 text-neutral-200 bg-neutral-900 border-neutral-700 focus:ring-neutral-600 focus:ring-2"
                  />
                </div>
                <div className="flex flex-col">
                  <span className="text-sm font-medium text-white">{t.split('(')[0].trim()}</span>
                  <span className="text-xs text-neutral-500 mt-1">Cost: {t.split('(')[1].replace(')', '')}</span>
                </div>
              </label>
            ))}
          </div>

          <div className="pt-6 mt-auto border-t border-neutral-800/50">
            <button 
              onClick={handleExecutePipeline}
              disabled={isExecuting}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 px-4 rounded-lg flex items-center justify-center space-x-2 transition-colors disabled:opacity-50"
            >
              {isExecuting ? <Loader2 className="w-4 h-4 animate-spin" /> : <PlayCircle className="w-4 h-4" />}
              <span>{isExecuting ? 'Engine Running...' : 'Commit Production Render'}</span>
            </button>
          </div>
        </div>

        {/* CARD 4: Production Archive & Delivery */}
        <div className="snap-center min-w-[380px] w-[26vw] bg-neutral-900/40 border border-neutral-800 rounded-2xl flex flex-col p-6 shadow-xl">
          <h2 className="text-white font-medium mb-4 flex items-center space-x-2">
            <span className="bg-neutral-800 text-xs px-2 py-1 rounded-full text-neutral-300">Step 4</span>
            <span>Archive & Delivery</span>
          </h2>
          <hr className="border-neutral-800 mb-6" />
          
          <div className="flex-1 flex flex-col overflow-y-auto custom-scrollbar pr-2 space-y-5">
            {/* Video Placeholder / Player */}
            <div className="w-full aspect-video bg-black border border-neutral-800 rounded-lg flex items-center justify-center overflow-hidden shrink-0">
              {videoSrc ? (
                <video key={videoSrc} src={videoSrc} controls autoPlay loop className="w-full h-full object-cover"></video>
              ) : (
                <span className="text-neutral-600 text-sm italic">{isExecuting ? 'Rendering...' : 'Watch your generated cinematic video here'}</span>
              )}
            </div>

            {/* Tracking Status list */}
            <div className="flex flex-col space-y-2 mt-4">
              {statusEvents.map((evt, idx) => (
                <div key={idx} className={`text-xs px-3 py-2 border rounded-full inline-flex w-fit items-center space-x-2
                  ${evt.type === 'pending' ? 'border-blue-500/30 text-blue-400 bg-blue-500/10' : 
                    evt.type === 'error' ? 'border-red-500/30 text-red-400 bg-red-500/10' : 
                    'border-emerald-500/30 text-emerald-400 bg-emerald-500/10'}`}
                >
                  {evt.type === 'pending' && <Loader2 className="w-3 h-3 animate-spin" />}
                  {evt.type === 'success' && <CheckCircle2 className="w-3 h-3" />}
                  {evt.type === 'error' && <XCircle className="w-3 h-3" />}
                  <span>{evt.status}</span>
                </div>
              ))}
              
              {statusEvents.length === 0 && !isExecuting && (
                <span className="text-xs text-neutral-600 italic">Awaiting execution...</span>
              )}
            </div>

            {/* Final Action Button */}
            {videoSrc && (
              <div className="pt-4 mt-auto">
                <a 
                  href={videoSrc} 
                  target="_blank" 
                  rel="noreferrer"
                  download="Naturo_Render.mp4"
                  className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-3 px-4 rounded-lg flex items-center justify-center space-x-2 transition-colors shadow-[0_0_15px_rgba(16,185,129,0.3)]"
                >
                  <LinkIcon className="w-4 h-4" />
                  <span>Download Video</span>
                </a>
              </div>
            )}
          </div>
        </div>

      </main>
    </div>
  )
}
