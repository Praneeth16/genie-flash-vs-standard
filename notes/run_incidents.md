# Run incidents

- 2026-10-31 15:04:20 to 15:04:24 local. Three in-flight requests stopped receiving stream events at the same moment (pair 98 STANDARD contribution-control-directed r4, pair 99 complaints-control-lookup r3 first mode, pair 100 complaints-control-lookup r5 first mode).
- Server side, Genie had completed both conversations it created (01f1d50e41681a6b9f137cd3be879d96 and 01f1d50e3fdd1be7b5c41be515946c66) in 7 to 9 seconds. The third request never created a conversation. So the client lost the stream. Genie did not fail.
- The client read timeout was 1800 s, so the runner sat idle for 23 minutes. I stopped it at 15:29, lowered the read timeout to 300 s and resumed. The resume reran only the three lost requests and the requests not yet started.
