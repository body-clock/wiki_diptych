# wiki_diptych
## [twitter bot](https://twitter.com/wiki_diptych)


This script gets a random image from 2 different random wikipedia articles. It joins the article titles together and attaches the photos to a tweet.

It works like this:

* Finds a page with at least 2 JPGs (this was my method of ensuring a high quality image. My thoughts were that - if a page has at        least 2 JPGs, it must be better documented which means better image. I made this up in my head.)
* This happens twice.
* Combine the titles of the pages into a single string (the tweet text) and attach the media (the images from the pages.)
* Tweet every 4hrs via Cron on Pi Zero W.

It worked flawlessly for a while, and then the flaws began to show.

* Occasionally it would only tweet a single image. After writing to a .log via cron on the Pi, I realized that the images were sometimes too large to be uploaded via Tweepy. I thought my idea was doomed, but quickly remembered that I could just write a function to resize the image if it was too large. So, I did that. And it works flawlessly forever now!
* If something goes wrong in your project, take it as an opportunity to learn. I used to be so scared of making mistakes & looking like I didn’t know what I was doing. If something breaks and you can’t figure it out, ask someone else. If they’re an experienced dev, chances are they’ve had to solve a similar problem themselves. If they’re an inexperienced dev, you can cry about your mistakes with them. Solidarity is key when you’re “in the woods” and don’t really know what to do next.
* Scope your project efficiently. Know & understand your strengths/weaknesses, and develop your idea around them. If you have no strengths, work on your weaknesses. If you think you have no weaknesses, you’re wrong.
