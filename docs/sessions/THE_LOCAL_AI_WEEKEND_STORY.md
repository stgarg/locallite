# The Local AI Weekend: Building a Multimodal Gateway from Scratch

*A weekend project that turned into a deep dive on what it actually takes to build AI infrastructure*

---

## The Setup

Picture this: It's a weekend in September 2025. I'm sitting with a new ARM laptop—one of those Snapdragon X Elite machines—and I have that familiar developer itch. You know the one. The "I wonder if I could build that myself" feeling.

I work at Azure AI during the week, surrounded by world-class AI infrastructure. But here's the thing about working on large-scale systems: you rarely get to feel the full weight of building something end-to-end. There are abstractions everywhere, teams for everything, and someone else always owns the part you're curious about.

So when I got this ARM laptop, I had a simple question: **What would it take to build my own AI gateway from scratch?**

Not because I thought I could build something better than what exists. Not because I had some grand vision of disrupting the AI space. But because I was genuinely curious about the pain points. What does it actually feel like to stitch these systems together? What are the sharp edges that users hit when they try to build AI into their applications?

And honestly? I was getting frustrated with always needing internet for basic AI tasks. Some of the stuff I want to automate on my laptop—document processing, basic text analysis, simple chat interactions—doesn't need GPT-4. It needs something good enough, fast enough, and local enough.

## The Hardware Constraint That Became an Opportunity

I had this ARM laptop. That was the constraint. Most AI tutorials assume you have a beefy x86 machine with an NVIDIA GPU. I had ARM64 and this thing called an NPU that I'd never actually used for anything real.

This is where the project got interesting. Instead of fighting the constraint, I decided to lean into it. What if I could make the NPU actually useful? What if ARM64 + NPU could be a legitimate platform for local AI?

The documentation was... sparse. Most of what I found was marketing material or academic papers. Very little "here's how you actually make this work in practice" content. This was either going to be a very short weekend project (because nothing would work) or a very educational one (because I'd have to figure everything out myself).

## The Scope Creep That Made Sense

I started with a simple goal: get embeddings working locally. Just embeddings. How hard could it be?

But once you start building AI infrastructure, the questions multiply:
- If I can do embeddings, why not chat completions?
- If I'm building an API, why not make it OpenAI-compatible so existing tools work?
- If I'm doing text processing, why not multimodal while I'm at it?

Each expansion felt natural. Not because I was trying to build everything, but because each piece unlocked something genuinely useful. Embeddings alone are limited. Embeddings + chat + multimodal = the foundation for pretty much any AI automation I might want to build later.

Plus, I'll admit it: there's something satisfying about building a system that can handle whatever you throw at it, rather than constantly hitting "this feature isn't supported" walls.

## The NPU Surprise

Here's where things got unexpectedly interesting. I expected the NPU to either not work at all or to be marginally useful. What I found was something much more nuanced.

For small batches (1-3 text inputs), the NPU was consistently 2.33x faster than CPU. For larger batches, it actually got slower. This wasn't documented anywhere. I discovered it by accident when I was testing different workloads.

This discovery changed everything. Instead of NPU vs. CPU, I could build NPU + CPU. Small batches go to NPU, large batches stay on CPU. Suddenly I had a system that was optimized for both interactive use (fast single queries) and batch processing (efficient bulk operations).

The lesson here: emerging hardware often has performance characteristics that aren't well understood yet. The people building the hardware know what it's capable of in theory. The people using it in production don't exist yet. There's a gap in between where you can discover things that will eventually become common knowledge.

## The Quantization Reality Check

I hit my first real wall with memory. Modern language models want 20-50GB of RAM. My laptop has 16GB total. Game over, right?

Not quite. Quantization changes the entire equation. A 20GB model becomes 4GB with Q4 quantization. Quality drops maybe 5-10%. Memory usage drops 5x. For most real-world tasks, this trade-off is a no-brainer.

But here's what surprised me: quantization isn't just about fitting in memory. On NPU hardware, quantized models are actually faster. The NPU is optimized for the kinds of operations that quantized models use. So I got smaller *and* faster.

This made me wonder: why isn't aggressive quantization more common? The benefits are obvious once you experience them. The tooling exists. Maybe it's just that most people have enough memory that they don't need to think about it. Or maybe the AI field is still young enough that "best practices" haven't fully propagated.

## The API Decision That Saved Everything

Early on, I made a decision that seemed constraining but turned out to be liberating: full OpenAI API compatibility. Instead of designing my own interface, I'd implement exactly what OpenAI's API provides.

This felt like giving up control. Why conform to someone else's design decisions? Why not build something better?

The answer became clear once I started testing. With OpenAI compatibility, existing tools just worked. Libraries, SDKs, applications—everything that already knew how to talk to OpenAI could talk to my local gateway. Zero integration work.

More importantly, it forced me to think about my system as a drop-in replacement for existing infrastructure. This constraint eliminated a lot of bad design choices. If you're aiming for compatibility, you can't make weird architectural decisions that would break existing assumptions.

## The Model Selection Adventure

I started with one model choice (Phi 3.5) but ended up with another (Gemma 3N). This wasn't due to poor planning—it was due to new information changing the optimal choice.

Phi 3.5 was smaller and faster. Gemma 3N was larger but multimodal. Both had ONNX versions. Both worked with quantization. The deciding factor was ecosystem maturity. The Gemma 3N ONNX implementation was more complete, better documented, and more actively maintained.

This is where working on a weekend project has advantages over enterprise development. I could change the model choice based on what I learned during implementation. No committee meetings, no architectural review boards, no backwards compatibility concerns. Just "this one works better, let's use it."

## The Abstraction Investment

One thing I did right from the beginning: I built good abstractions. `BaseModel` for different AI models, `UnifiedRequest`/`UnifiedResponse` for API handling, modular routing for different capabilities.

This turned out to be crucial when I changed the model choice. The architecture didn't need to change, just the implementation behind the abstraction. Good abstractions early meant flexibility later.

This is something I've noticed in successful weekend projects: the ones that start with good structure can evolve and grow. The ones that start with quick hacks hit walls quickly.

## What This Actually Teaches About AI Infrastructure

After building this system, I have a much better appreciation for what commercial AI providers are solving. It's not just about having good models (though that's important). It's about:

**Performance optimization across diverse workloads**: That NPU batch size discovery took hours of testing. Multiply that by dozens of hardware configurations and hundreds of model types.

**Memory management at scale**: Quantization trade-offs seem obvious in retrospect, but someone had to figure out what "acceptable quality loss" means for different use cases.

**API design that doesn't break**: OpenAI's API seems simple until you try to implement it completely. There are subtle edge cases and compatibility requirements everywhere.

**Integration complexity**: Making everything work together—models, hardware acceleration, API compatibility, error handling—is the real challenge. Each piece is manageable; the system is complex.

## The Weekend Project Reality

This was supposed to be a weekend project. It's now been several weekends. Not because things are broken, but because each working piece reveals new possibilities.

The embeddings work great. The chat API is ready for the actual model integration. The NPU acceleration exceeded expectations. The system is genuinely useful for my local automation needs.

But more than that, I now understand what it feels like to build AI infrastructure from scratch. The pain points are real, but they're solvable. The performance optimization is fascinating. The integration challenges are significant but not insurmountable.

## The "Vibe Coding" Experiment

I've been building this with AI assistance—what some people call "vibe coding." Human direction, AI implementation, constant iteration and refinement.

The results have been impressive. Complex systems that would have taken weeks to build solo are coming together in days. The AI handles the boilerplate, the research, the documentation. I handle the architecture decisions, the problem-solving, the creative leaps.

This feels like a glimpse of how software development might work in the future. Not AI replacing developers, but AI amplifying what developers can accomplish. The weekend project scale that used to be "simple script" can now be "complete system."

## What's Next

The core system works. NPU acceleration works. API compatibility works. The foundation is solid.

Next: actually integrate the Gemma 3N model and see how multimodal AI works in practice. Then start building the automation tasks that motivated this whole project.

But the real value has already been captured: understanding what it takes to build AI infrastructure, feeling the pain points firsthand, and discovering that a weekend warrior with good tools can build systems that would have required teams just a few years ago.

That's a story worth telling.

---

*Built over several weekends in September 2025, powered by curiosity and an ARM laptop.*