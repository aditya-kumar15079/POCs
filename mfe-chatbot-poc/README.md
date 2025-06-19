# Microfrontend via Webcomponents POC

## Steps to run the app
- npm i

- npm run build
 -- It will generate dist/chat-bot.iife.js (mfe build)

- npx serve .

 -- It will serve the test.html file which hosts the mfe. mfe is taken directly from path ./dist/chat-bot.iife.js

 ### To host the mfe on another app just paste the built iife.js file to the host assets folder and load the mfe js by script tag.
 - Copy chat-bot.iife.js and style.css into the host app's public folder

- In the host app HTML or main layout:<br>
< chat-bot></ chat-bot><br>
< script src="/assets/chat-bot.iife.js"></ script>


If using frameworks like React, Angular, etc., include the < chat-bot></ chat-bot> element in the appropriate part of your layout (e.g. JSX dangerouslySetInnerHTML, or in index.html).



