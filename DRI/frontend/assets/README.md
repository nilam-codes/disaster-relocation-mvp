# assets/

`dri-logo.jpeg` — your logo, already placed here and wired into every page header
and the landing page.

## Background image

You mentioned your designer's background image would be sent separately — it
wasn't attached, so `index.html` currently uses a CSS gradient + subtle
contour-line texture as a stand-in (same green/beige palette, no AI-generated
image, nothing to swap out logically — just flat CSS).

To drop in the real background image once you have it:

1. Save it as `frontend/assets/hero-background.jpg` (or `.png`).
2. Open `frontend/index.html`, find the `.hero` rule in the `<style>` block, and add:

```css
.hero {
  background-image: url('assets/hero-background.jpg');
  background-size: cover;
  background-position: center;
}
```

Keep the `.hero::before` texture layer or remove it — either works with a
photo background; you may want to lower its opacity if the photo is busy.
