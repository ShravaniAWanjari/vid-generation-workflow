import { useState, useRef, useEffect } from 'react'
import { UploadCloud, CheckCircle2, Loader2, PlayCircle, Link as LinkIcon, RefreshCw, XCircle, Lightbulb } from 'lucide-react'

export default function App() {
  const [demoMode, setDemoMode] = useState(true)
  const [showDemoBubble, setShowDemoBubble] = useState(false)
  
  // Card 1: Asset Assembly
  const [productImage, setProductImage] = useState(null)
  const [styleVideo, setStyleVideo] = useState(null)
  const [rawIntent, setRawIntent] = useState('')
  const [isCompiling, setIsCompiling] = useState(false)
  
  // Card 2: Boxed Prompt Workspace
  const [compiledPrompt, setCompiledPrompt] = useState('')
  const [extractedProductName, setExtractedProductName] = useState('')
  const [executedProductName, setExecutedProductName] = useState('')
  
  // Card 3: Video Generation Engine
  const tiers = [
    "Tier 1: Decent Videos ($0.03)",
    "Tier 2: Special Product Movements & Hyper-Realism ($0.12)",
    "Tier 3: Precision Cinematic Shots ($0.25)"
  ]
  const [selectedTier, setSelectedTier] = useState(tiers[1])
  const [executedTier, setExecutedTier] = useState(tiers[1])
  
  // Card 4: Production Archive & Delivery
  const [isExecuting, setIsExecuting] = useState(false)
  const [statusEvents, setStatusEvents] = useState([])
  const [webViewLink, setWebViewLink] = useState('')
  const [hasError, setHasError] = useState(false)

  const handleCompilePrompt = async () => {
    if (!productImage || !rawIntent) {
      alert('Please provide a Product Image and Raw Intent.')
      return
    }
    
    setIsCompiling(true)
    console.log("Starting compilation process...");
    
    try {
      const formData = new FormData();
      formData.append('product_image', productImage);
      if (styleVideo) {
        formData.append('style_video', styleVideo);
      } else {
        formData.append('style_video', new File([""], "empty.mp4", { type: "video/mp4" }));
      }
      formData.append('raw_intent', rawIntent);

      const response = await fetch('/api/compile-prompt', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        let errorMsg = 'Compilation failed';
        try {
          const errorData = await response.json();
          errorMsg = typeof errorData.detail === 'string' 
            ? errorData.detail 
            : JSON.stringify(errorData.detail || errorData);
        } catch(e) {
          errorMsg = `HTTP Error ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMsg);
      }

      const data = await response.json();
      
      setExtractedProductName(data.product_name || "Unknown Product");
      setCompiledPrompt(data.compiled_prompt || "");
      console.log(`Prompt compilation finished successfully. Extracted Product: ${data.product_name}`);
    } catch (error) {
      console.log("Backend API not available. Falling back to simulation...", error);
      
      // Attempt to call Gemini Vision directly from the frontend if API key is provided
      const apiKey = import.meta.env.VITE_GEMINI_API_KEY;
      let simulatedProductName = "";
      
      if (apiKey && productImage) {
        try {
          const reader = new FileReader();
          reader.readAsDataURL(productImage);
          await new Promise(resolve => reader.onload = resolve);
          const base64Image = reader.result.split(',')[1];
          
          const geminiResponse = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              contents: [{
                parts: [
                  { text: "Identify the exact product name from this image. Output ONLY the short product name (e.g. 'Radiating Face Cream', 'Kumkumadi Face Cream'). Do not include any other text." },
                  { inlineData: { mimeType: productImage.type || 'image/png', data: base64Image } }
                ]
              }]
            })
          });
          
          const geminiData = await geminiResponse.json();
          simulatedProductName = geminiData.candidates[0].content.parts[0].text.trim();
          console.log("Direct Gemini Vision extraction:", simulatedProductName);
        } catch (err) {
          console.error("Direct Gemini call failed:", err);
        }
      }
      
      if (!simulatedProductName) {
        const baseName = productImage.name.split('.')[0];
        simulatedProductName = baseName.replace(/_/g, " ").replace(/-/g, " ");
        console.log("Fell back to filename extraction:", simulatedProductName);
      }
      
      const simulatedPrompt = `A cinematic macro commercial shot. The camera is positioned in a static placement, framing the product container in the center. In a seamless, slow pan/zoom out motion, the product container remains perfectly still, static, and unaltered in the center. Highly detailed textures, soft studio lighting, high-end commercial advertisement style. \n\n(Intent: ${rawIntent})`;
      
      setExtractedProductName(simulatedProductName);
      setCompiledPrompt(simulatedPrompt);
      console.log(`Fallback simulation finished. Extracted Product: ${simulatedProductName}`);
    } finally {
      setIsCompiling(false);
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
    
    console.log("Executing video generation pipeline...");
    console.log(`Selected Tier: ${selectedTier}`);

    // Simulate Server-Sent Events flow
    const sequence = [
      { msg: "Extracting Keyframes...", delay: 1500, evtType: 'success' },
      { msg: "Compiling Spatial VLM Prompt...", delay: 3000, evtType: 'success' },
      { msg: "Archiving to Studio Drive (Upcoming feature)", delay: 4500, evtType: 'upcoming' },
    ];

    sequence.forEach(({ msg, delay, evtType }) => {
      setTimeout(() => {
        console.log(`Pipeline Status: ${msg}`);
        setStatusEvents(prev => [...prev, { status: msg, type: evtType }]);
      }, delay);
    });

    setTimeout(() => {
      console.log("Pipeline execution finished successfully.");
      setStatusEvents(prev => [...prev, { status: "Executed: SUCCESS", type: 'success' }]);
      setExecutedTier(selectedTier); // Lock in the tier for the video player
      setExecutedProductName(extractedProductName || productImage.name.split('.')[0]); // Lock in the product name
      setWebViewLink('local-demo'); // Triggers local video loading
      setIsExecuting(false);
    }, 6500);
  }

  const getDemoVideoSrc = () => {
    // Read videos provided by vite.config.js global define
    const availableVideos = typeof __AVAILABLE_VIDEOS__ !== 'undefined' ? __AVAILABLE_VIDEOS__ : [];
    const globalFallback = availableVideos.length > 0 ? `/${availableVideos[0]}` : "";

    if (!productImage && !executedProductName) return globalFallback;
    
    // Use the locked-in product name from execution time, preventing mid-generation switches
    const nameSource = executedProductName || extractedProductName || productImage.name.split('.')[0];
    const baseName = nameSource;
    
    // Extract significant words (longer than 2 chars, ignore common terms)
    const searchWords = baseName.toLowerCase().replace(/[^a-z0-9]/g, ' ').split(' ').filter(w => w.length > 2 && w !== 'cream' && w !== 'face' && w !== 'product' && w !== 'gel' && w !== 'the');
    
    let tierNum = 1;
    if (executedTier.includes("Tier 2")) tierNum = 2;
    if (executedTier.includes("Tier 3")) tierNum = 3;

    // Score videos based on how many search words they contain
    let bestMatchScore = 0;
    let matchingVideos = [];
    
    availableVideos.forEach(v => {
      const vNormalized = v.toLowerCase();
      let score = 0;
      searchWords.forEach(w => {
        if (vNormalized.includes(w)) score++;
      });
      
      // Exact match bonus
      if (vNormalized.startsWith(baseName.toLowerCase().replace(/ /g, '_'))) score += 5;
      
      if (score > 0) {
        if (score > bestMatchScore) {
          bestMatchScore = score;
          matchingVideos = [v];
        } else if (score === bestMatchScore) {
          matchingVideos.push(v);
        }
      }
    });

    if (matchingVideos.length === 0) {
      // Global fallback if no product videos exist
      return globalFallback;
    }

    // Among the best matches, look for the requested tier
    const tierMatch = matchingVideos.find(v => v.toLowerCase().includes(`tier${tierNum}`));
    if (tierMatch) return `/${tierMatch}`;
    
    // If exact tier not found, check if the video has no tier specified
    const genericMatch = matchingVideos.find(v => !v.toLowerCase().includes('tier'));
    if (genericMatch) return `/${genericMatch}`;
    
    // Otherwise return the first matching video for this product
    return `/${matchingVideos[0]}`; 
  };

  const videoSrc = !demoMode ? webViewLink : (webViewLink ? getDemoVideoSrc() : "");

  return (
    <div className="flex flex-col h-[100dvh] w-full bg-neutral-950 text-neutral-400 overflow-hidden font-sans">
      
      {/* Fixed Top Navbar */}
      <nav className="h-16 shrink-0 border-b border-neutral-800 bg-neutral-950 flex items-center justify-between px-4 md:px-8 z-50 shadow-sm">
        <div className="flex items-center space-x-3">
          <PlayCircle className="text-white w-6 h-6" />
          <h1 className="text-white text-xs sm:text-sm md:text-base font-semibold tracking-wide truncate max-w-[150px] sm:max-w-none">NOCT CREATIVE DISPATCH</h1>
        </div>
        <div className="flex items-center space-x-2 md:space-x-6 relative">
          <div 
            className="flex items-center space-x-2 md:space-x-3 cursor-not-allowed opacity-80" 
            onClick={() => {
              setShowDemoBubble(true);
              setTimeout(() => setShowDemoBubble(false), 2500);
            }}
          >
            <span className="text-xs md:text-sm font-medium text-neutral-300 whitespace-nowrap pointer-events-none">Demo Mode</span>
            <div className="relative pointer-events-none">
              <input 
                type="checkbox" 
                className="sr-only" 
                checked={true} 
                readOnly
              />
              <div className="block w-10 h-6 rounded-full transition-colors bg-neutral-600"></div>
              <div className="dot absolute left-1 top-1 bg-white w-4 h-4 rounded-full transition-transform transform translate-x-4"></div>
            </div>
          </div>
          
          {showDemoBubble && (
            <div className="absolute top-12 right-0 md:right-auto bg-neutral-800 text-xs text-white px-3 py-2 rounded shadow-lg whitespace-nowrap z-50">
              Production Workflow under development
              <div className="absolute -top-1 right-6 w-2 h-2 bg-neutral-800 transform rotate-45"></div>
            </div>
          )}
        </div>
      </nav>

      {/* Horizontal / Vertical Stepper Workspace */}
      <main className="flex-1 flex flex-col md:flex-row overflow-y-auto md:overflow-x-auto md:overflow-y-hidden snap-y snap-mandatory md:snap-x gap-8 md:gap-16 py-8 px-4 md:p-10 md:px-16 custom-scrollbar items-stretch pb-12 w-full">
        
        {/* CARD 1: Asset Assembly */}
        <div className="snap-start md:snap-center shrink-0 w-full min-h-[calc(100dvh-8rem)] md:min-h-0 md:min-w-[500px] md:w-[45vw] bg-neutral-900/40 border border-neutral-800 rounded-2xl flex flex-col p-6 md:p-8 shadow-xl">
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
              <div className="relative border-2 border-dashed border-neutral-800 hover:border-neutral-600 bg-neutral-900/50 rounded-lg p-6 flex flex-col items-center justify-center cursor-pointer transition-colors">
                <input type="file" className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" onChange={(e) => setStyleVideo(e.target.files[0])} />
                <div className="text-center">
                  <div className="flex flex-col items-center">
                    <span className="text-xs text-neutral-500 mb-1">Style Video <span className="bg-neutral-800 text-neutral-400 px-1.5 rounded ml-1">Optional</span></span>
                  </div>
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
        <div className="snap-start md:snap-center shrink-0 w-full min-h-[calc(100dvh-8rem)] md:min-h-0 md:min-w-[500px] md:w-[45vw] bg-neutral-900/40 border border-neutral-800 rounded-2xl flex flex-col p-6 md:p-8 shadow-xl">
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
        <div className="snap-start md:snap-center shrink-0 w-full min-h-[calc(100dvh-8rem)] md:min-h-0 md:min-w-[500px] md:w-[45vw] bg-neutral-900/40 border border-neutral-800 rounded-2xl flex flex-col p-6 md:p-8 shadow-xl">
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
              <span>{isExecuting ? 'Engine Running...' : 'Generate'}</span>
            </button>
          </div>
        </div>

        {/* CARD 4: Production Archive & Delivery */}
        <div className="snap-start md:snap-center shrink-0 w-full min-h-[calc(100dvh-8rem)] md:min-h-0 md:min-w-[380px] md:w-[26vw] bg-neutral-900/40 border border-neutral-800 rounded-2xl flex flex-col p-6 shadow-xl">
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
                    evt.type === 'upcoming' ? 'border-amber-500/30 text-amber-400 bg-amber-500/10' :
                    'border-emerald-500/30 text-emerald-400 bg-emerald-500/10'}`}
                >
                  {evt.type === 'pending' && <Loader2 className="w-3 h-3 animate-spin" />}
                  {evt.type === 'success' && <CheckCircle2 className="w-3 h-3" />}
                  {evt.type === 'error' && <XCircle className="w-3 h-3" />}
                  {evt.type === 'upcoming' && <Lightbulb className="w-3 h-3" />}
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
