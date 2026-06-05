# Demo Review Session

This example shows the intended user experience for exam review. It is synthetic and does not contain private course material.

## User

```text
Use ai-study-workflow. Read this lecture PPTX first.
I want fast exam review. Start with a 10-minute closed-book diagnostic.
Do not show answers until I respond.
```

## Agent

```text
Source card
- Scope: networking chapter, 89 slides
- Usable text: good
- Visual checks: 30 diagram-heavy slides should be rendered before final diagram explanations
- Caveat: optional appendix slides need exam-scope confirmation

Mode
- Exam review, because you asked for fast score improvement.

Closed-book diagnostic
Answer briefly. Do not look at your notes.

1. What is a protocol? Name the parts that make the definition complete.
2. What is the difference between the network edge and the network core?
3. Why does packet switching create queueing delay?
4. What does L/R represent in store-and-forward transmission?
5. Packet switching and circuit switching differ in how they use resources. State the key contrast.
6. What four components make up nodal delay?
7. What does traffic intensity measure, and why is it risky when it approaches 1?
8. What determines end-to-end throughput when multiple links are on the path?
9. Name the five Internet protocol layers in order.
10. In encapsulation, what is added to message M, and why?

Stop here. Send your answers before I grade or explain.
```

## User

```text
1. A protocol is a set of communication rules.
2. Edge is user devices, core is routers and ISPs.
3. Queueing happens when packets arrive faster than the link can send them.
4. L/R is the time to send L bits over rate R.
5. Packet switching shares the link; circuit switching reserves it.
6. Processing, queueing, transmission, propagation.
7. Traffic intensity is how busy the link is. Near 1 means delay gets bad.
8. The slowest link usually limits throughput.
9. Application, transport, network, link, physical.
10. Headers are added so each layer can deliver its service.
```

## Agent

```text
Score: 8.0/10

correct:
- Q3: Correct causal explanation for queueing delay.
- Q4: Correct: L/R is transmission delay for pushing L bits onto a link with rate R.
- Q5: Correct high-level contrast between packet and circuit switching.
- Q6: Correct four-part nodal delay list.
- Q9: Correct five-layer order.

missing:
- Q1: "communication rules" is too thin. A complete protocol answer should include message format/order and actions taken on send/receive events.
- Q2: Network core needs "interconnected routers" and packet forwarding/routing, not just ISPs.
- Q7: Needs the formula idea: traffic intensity is usually La/R, and queueing delay grows sharply as it approaches 1.
- Q8: "slowest link" is a good first answer, but end-to-end throughput can also be limited by sender, receiver, congestion, and shared bottlenecks.
- Q10: Needs the term encapsulation: each layer wraps the higher-layer data with its own header to create a new protocol data unit.

incorrect:
- None severe.

likely cause:
- You know the concepts verbally, but several answers miss exact exam keywords.

next drill:
1. Rewrite Q1 using the words message, order, event, and action.
2. Solve one throughput bottleneck scenario with three links.
3. Explain encapsulation using the terms message, segment, datagram, frame, and header.

card candidates:
- source: slide-protocol
  front: What makes a protocol definition complete?
  back: Message format/order plus actions taken when messages are sent, received, or other events occur.
- source: slide-delay
  front: Why does queueing delay grow sharply when traffic intensity approaches 1?
  back: The arrival rate approaches service capacity, so the queue has little slack and waiting time rises rapidly.
- source: slide-encapsulation
  front: What does encapsulation add at each layer?
  back: A layer-specific header that lets that layer implement its service for the higher-layer data.
```

## User

```text
Generate Anki CSV drafts from these three real mistakes.
```

## Agent

```csv
deck,tags,type,front,back,source
Computer Networking,chapter1 protocol,basic,What makes a protocol definition complete?,"Message format/order plus actions taken when messages are sent, received, or other events occur.",slide-protocol
Computer Networking,chapter1 delay,basic,Why does queueing delay grow sharply when traffic intensity approaches 1?,"The arrival rate approaches service capacity, so the queue has little slack and waiting time rises rapidly.",slide-delay
Computer Networking,chapter1 encapsulation,basic,What does encapsulation add at each layer?,"A layer-specific header that lets that layer implement its service for the higher-layer data.",slide-encapsulation
```
