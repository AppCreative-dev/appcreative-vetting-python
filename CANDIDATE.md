# AppCreative engineering exercise (Python)

Thanks for doing this. It's a work sample, not a quiz. You'll do it on your
own, in one sitting of about 90 minutes, while recording your screen and
talking through what you're doing. Use whatever AI coding tool you normally
use. We care more about how you check the AI's work than how fast you go.
If you don't finish everything, submit what you have.

Plan for about two hours in one sitting: about 20 minutes of setup, then
the 90-minute exercise. The clock starts only after setup.

If your submission is shortlisted, we'll book a 20-minute call to talk
through the choices you made.

## Setup (about 20 minutes, before the clock starts)

1. **GitHub account.** Sign in to github.com, or create a free account.
2. **Your own private copy.** On the exercise repository, click **Use this
   template** → **Create a new repository**. Choose **Private**, then
   **Create repository**. Do all your work in this copy.
3. **Give us access.** In your new repository, go to **Settings** →
   **Collaborators** → **Add people**, and add **AppCreative-dev**.
4. **AI tool.** If you'll use GitHub Copilot, turn it on at
   github.com/settings/copilot (the free plan works). New accounts must do
   this first, or every chat fails with "Sorry, something went wrong."
   Any AI tool a client could approve is fine. Don't paste this code into a
   public chatbot that keeps what you send it.
5. **Open a codespace.** In your repository, click **Code** → **Codespaces**
   → **Create codespace on main**. The first build takes about 5 minutes.
   - If asked whether you trust the authors, choose **Trust Folder & Continue**.
   - If your editor or AI tool offers to create or configure a Python
     environment, say **no**. Python is already set up.
6. **Check it works.** In the terminal, run `bash start.sh` and wait for
   four ✅ lines. Send your AI tool one test message.
7. **Recording.** Set up a screen recorder that captures your screen and
   your voice, such as Loom. You'll need to share a viewable link at the end.

## The rules

- One sitting, about 90 minutes, recorded from start to finish.
- Talk through what you're doing and why, especially when you check or
  reject something the AI suggested.
- Work on your own. AI tools are expected; other people are not.

## Doing the exercise

1. **Start your recording**, then run `bash begin.sh` to start the clock.
2. Do Parts 1–3 below.
3. Answer the four questions in **ANSWERS.md**.
4. Export your AI chat history into the **submission** folder. In Copilot
   Chat, use the **...** menu or press F1 and type **Export Chat**. If your
   tool can't export, copy the conversation into `submission/ai-chat.md`.
5. Stop your recording and copy its link.
6. Run `bash submit.sh` and follow its prompts. It checks your work and
   uploads everything to your repository.

## The system

A small online outdoor-gear shop:

- **orders** (port 8001): returns an order plus product recommendations.
- **recommendations** (port 8002): asks an AI model which products a customer is likely to want next.
- **practice AI model** (port 8003): stands in for a real AI provider. Treat it as an outside service you don't control.
- **Grafana** (port 3000): where traces show up. Open it from the PORTS tab.

Code changes reload automatically. Try it: `curl localhost:8001/orders/A1001`

## Part 1: Fix and extend (30 min)

The recommendations feature is half done, and the test in `tests/` fails.
Finish it so that:

1. The test passes (`python -m pytest tests`).
2. `GET /orders/{id}` returns the top 3 recommendations, each with its
   product id, name and the model's reason.
3. The orders page stays fast, under 2 seconds, even when the AI model is
   having a bad day. When the model is too slow, return the customer's top 3
   best-selling products they haven't bought (see `best_seller_rank`), with
   the reason "Popular with other customers".

## Part 2: Instrument (20 min)

Right now traces stop at the orders service. Make one request show up in
Grafana as **one connected trace** through orders, recommendations and the
call to the AI model.

- The AI model call should be easy to spot and say which model was used and
  how many tokens it took (the model's reply includes `usage`).
- Keep sensitive data out of telemetry and logs.
- Send telemetry to the collector at `http://localhost:4318` (it's already
  running).
- To view traces: Grafana → Explore → choose **Tempo** → Search.

## Part 3: Alert (20 min)

`alert-exercise/orders_week.png` is a chart of last week's data for the orders
service, and `orders_week.csv` has the minute-by-minute numbers. There was
**one real incident** last week. Everything else was harmless.

Write one alert rule in `alert-exercise/my-alert.yaml` that would have caught
the incident without paging anyone for the rest. Give it a severity and a
message an on-call engineer would understand.

## Checking your own work

You can run `bash check.sh` at any time. It's a quick health check that your
work builds and runs, not a grade. Checking that your work meets the brief is
part of the exercise: after you submit, we look at your code, your recording,
your AI chat and your written answers.
