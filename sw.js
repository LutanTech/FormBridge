const CACHE_NAME = "formbridge-v1";
const urlsToCache = [
  "/",
  "/assets/logo.png",
  "/assets/images/logo-nbg.png"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
