---
name: frontend-ui
description: Build complete frontend interfaces including pages, components, layouts, styling, and animations. Use for scalable, responsive web application UIs.
---

# Frontend UI Skill

## Purpose
This skill focuses on **end-to-end frontend construction** for modern web applications. It covers **page composition, reusable components, layout systems, styling strategies, and animations**, with an emphasis on clarity, responsiveness, and performance.

Use this skill when building or structuring frontend UIs in frameworks such as **Next.js (App Router)** or similar component-based systems.

---

## Instructions

### 1. Pages
- Structure pages using clear layout hierarchies
- Separate page-level logic from reusable components
- Ensure consistent spacing and visual rhythm
- Follow mobile-first design principles

### 2. Components
- Build reusable, composable components
- Keep components focused on a single responsibility
- Avoid unnecessary state and side effects
- Use clear naming and predictable props

### 3. Layout
- Use modern layout techniques (Flexbox, Grid)
- Support responsive breakpoints (mobile, tablet, desktop)
- Maintain alignment consistency across pages
- Ensure accessibility and readable content flow

### 4. Styling
- Apply consistent design tokens (spacing, colors, typography)
- Use scalable styling approaches (CSS Modules, Tailwind, scoped CSS)
- Avoid inline styles for complex layouts
- Ensure contrast and readability

### 5. Animations
- Add animations to enhance, not distract
- Use GSAP or CSS animations where appropriate
- Trigger animations on load, scroll, or interaction
- Ensure animations are smooth and performant
- Avoid layout thrashing and blocking renders

---

## Best Practices

- Mobile-first, responsive by default
- Reuse components instead of duplicating markup
- Keep animation duration short and intentional
- Avoid over-animating critical UI paths
- Optimize for performance without changing features
- Keep UI logic predictable and maintainable

---

## Example Structure

```tsx
// Page
<main className="page">
  <Header />
  <section className="content">
    <AnimatedTitle />
    <CardGrid />
  </section>
</main>

// Component
<section className="card">
  <h2 className="animate-fade-in">Title</h2>
  <p className="animate-slide-up">Description</p>
</section>
