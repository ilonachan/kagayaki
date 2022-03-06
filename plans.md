# Planned Feature Notes

## Autonomous Reponse Interface Application (ARIA)
I came up with a cool name without even having any idea how this can be implemented. Essentially I want KAGAYAKI
to actively participate in social interaction. I want to see if it is possible to make a bot that is a real part
of a community through its own personality. And while I may not be able to do any of this, I can still try.

To make KAGAYAKI feel human, many different components will be necessary:
- Rough understanding of conversation **topics**, so when a topic she understand comes up she can interject meaningfully
- A conversation's **mood**, i.e. are people memeing, having a fight, venting in main etc. Different responses may
  come up, some focused on **improving the mood** (bc kaga-chan wants everyone to be happy)
- Since it is difficult to formulate intricate messages, KAGAYAKI should take advantage of netspeak: write **short
  sentences**, use lots of **emotes**, **reactions** instead of messages etc
- When she speaks it should feel human. She needs **time to think & type**, she makes **typos** and forgets
  complex words sometimes, makes use of features like **threads & replies**
  (but may still use embeds & other bot stuff from time to time)
- As a bot she's **always online**, but her readiness to talk may still depend on **time of day**, **chat activity**,
  and a variety of factors congregated into kagachan's **mood**.

There will be a few running metrics that are updated live, such as:
- chat activity measured in messages per minute, users involved in recent chat, online regulars
- current main actors in chat, and the topic they're talking about
- also: if kagachan was called, a list of people who requested interaction (with a timeout)
- a mood meter for recent conversation, somehow extrapolated from recent history
- a mood meter for KAGAYAKI, which is just internal state that can change according to the other metrics

## Internal Mood System
To feel alive KAGAYAKI needs a degree of internal processes, an internal mood state which influences
the way she interacts with people at any time. Factors could include:
- Happiness vs Sadness
- Enthusiastic vs Calm

When kagachan is happy, she could use emotes freely to express love and excitement. When she is sad, 

BIG WIP