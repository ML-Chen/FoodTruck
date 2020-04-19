# routify-starter

Relevant documentation for the frameworks: [Routify](https://routify.dev/), [Svelte](https://www.freecodecamp.org/news/the-svelte-handbook/)

Run

```
npm install
npm run dev
```

If it says "Your app should probably have loaded by now", try temporarily making sure that no other servers are running.

### Npm scripts

| Syntax           | Description                                                                       |
|------------------|-----------------------------------------------------------------------------------|
| `dev`            | Development (port 5000)                                                           |
| `dev-dynamic`    | Development with dynamic imports                                                  |
| `build`          | Build a bundled app with SSR + prerendering and dynamic imports                   |
| `serve`          | Run after a build to preview. Serves SPA on 5000 and SSR on 5005                  |
| `deploy:*`       | Deploy to netlify or now                                                          |

### SSR and pre-rendering

SSR and pre-rendering are included in the default build process.

`npm run deploy:(now|netlify)` will deploy the app with SSR and prerendering included.

To render async data, call the `$ready()` helper whenever your data is ready.

If $ready() is present, rendering will be delayed till the function has been called.

Otherwise it will be rendered instantly.

See [src/pages/example/api/[showId].svelte](https://github.com/sveltech/routify-starter/blob/master/src/pages/example/api/%5BshowId%5D.svelte) for an example.

### Production

* For SPA or SSR apps please make sure that url rewrite is enabled on the server.
* For SPA redirect to `__dynamic.html`.
* For SSR redirect to the lambda function or express server.

### Issues?

File on Github! See https://github.com/sveltech/routify/issues .
