Project Moth

A small experiment in keeping private prompts off the cloud.

I wanted to see if a router could look at a prompt and decide whether a local model could handle it, or whether it should go to a (simulated) cloud service. The idea is that anything sensitive stays on my machine.

How it works

Each prompt gets checked for how complex it is, whether it looks private, and roughly what it would cost to run. The router then picks local or cloud, and I log the decision so I can see why it chose what it did. Local prompts run through Ollama with Gemma. Cloud routing is simulated, and no cloud API is ever called.

What I found

I ran 6 synthetic prompts through it:

4 went local, 2 went to the simulated cloud (67% / 33%)
Routing decisions are fast: about 0.56 ms on average
Local inference is slow: 3 successful local responses averaged about 94 seconds. The two simple prompts took about 104 seconds each, and the privacy prompt about 73 seconds.

Limitations
Six prompts is a tiny sample, and they’re synthetic, so none of this should be read as general performance.
Local inference on my machine is slow. The routing logic isn’t the bottleneck, the model is.
Cloud latency is simulated, not measured.
Stack

Python, FastAPI, Ollama, Gemma, Pytest

https://ynithyanjali.github.io/project-moth-privacyaware-router/
