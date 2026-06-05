---
name: Financial Guidance System
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#5d3f3c'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#926f6b'
  outline-variant: '#e7bdb8'
  surface-tint: '#c00014'
  primary: '#ba0013'
  on-primary: '#ffffff'
  primary-container: '#e31e24'
  on-primary-container: '#fffafa'
  inverse-primary: '#ffb4ab'
  secondary: '#565e74'
  on-secondary: '#ffffff'
  secondary-container: '#dae2fd'
  on-secondary-container: '#5c647a'
  tertiary: '#4e5c72'
  on-tertiary: '#ffffff'
  tertiary-container: '#67758b'
  on-tertiary-container: '#fcfbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad6'
  primary-fixed-dim: '#ffb4ab'
  on-primary-fixed: '#410002'
  on-primary-fixed-variant: '#93000d'
  secondary-fixed: '#dae2fd'
  secondary-fixed-dim: '#bec6e0'
  on-secondary-fixed: '#131b2e'
  on-secondary-fixed-variant: '#3f465c'
  tertiary-fixed: '#d5e3fd'
  tertiary-fixed-dim: '#b9c7e0'
  on-tertiary-fixed: '#0d1c2f'
  on-tertiary-fixed-variant: '#3a485c'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 0.25rem
  sm: 0.5rem
  md: 1rem
  lg: 1.5rem
  xl: 2rem
  2xl: 3rem
  3xl: 4rem
  gutter: 1.5rem
  margin-mobile: 1rem
  margin-desktop: 5rem
---

## Brand & Style
The brand personality is authoritative yet accessible, designed to instill confidence in users navigating complex mutual fund data. This design system follows a **Corporate / Modern** aesthetic, prioritizing clarity and precision to reflect the reliability of a premier financial institution. 

The visual strategy focuses on extreme legibility and "breathable" layouts. By utilizing high-quality whitespace and a restricted color palette, the interface reduces cognitive load. The emotional response should be one of security and professional ease—moving away from the cluttered density of traditional banking apps toward a refined, fintech-forward experience inspired by modern investment platforms.

## Colors
The palette is rooted in the heritage HDFC Red, used strategically for primary actions and brand presence. 

- **Primary (#E31E24):** Reserved for high-impact calls to action and active states. 
- **Secondary (#0F172A):** Used for primary headings and critical UI text to ensure maximum contrast and an "Enterprise" feel.
- **Surface Tones:** A progression of cool grays (#F8FAFC to #F1F5F9) is used to differentiate content sections without the need for heavy borders.
- **Functional Colors:** Success (Green), Warning (Amber), and Error (Red) should be used in muted tints for backgrounds and high-chroma for icons/text to maintain accessibility.

## Typography
Inter is selected for its exceptional legibility and systematic "neutrality," making it ideal for data-heavy fintech applications. 

Tighten letter spacing on larger headlines to create a premium, editorial feel. Body text uses a generous line height (1.5x) to ensure long FAQ answers remain readable. Use `label-md` for small metadata or section eyebrows to provide structural hierarchy without overwhelming the primary content.

## Layout & Spacing
The system employs a **Fixed Grid** for desktop (max-width 1200px) and a **Fluid Grid** for mobile devices. 

- **Desktop:** 12-column grid with 24px (1.5rem) gutters.
- **Tablet:** 8-column grid with 20px gutters.
- **Mobile:** 4-column grid with 16px gutters and 16px side margins.

Spacing follows an 8pt rhythm (multiples of 4px). Use `3xl` (64px) spacing between major sections on desktop to maintain the premium, high-whitespace aesthetic. Components like cards should use `lg` (24px) internal padding to feel spacious.

## Elevation & Depth
Depth is conveyed through **Tonal Layers** and **Ambient Shadows**. Instead of traditional harsh shadows, this design system uses soft, diffused shadows with a slight blue-gray tint to match the secondary color.

- **Level 0 (Base):** #FFFFFF background.
- **Level 1 (Cards/Inputs):** Background #FFFFFF with a 1px border (#F1F5F9) or a very soft shadow (0px 4px 20px rgba(15, 23, 42, 0.05)).
- **Level 2 (Dropdowns/Modals):** Background #FFFFFF with a more pronounced shadow (0px 10px 30px rgba(15, 23, 42, 0.1)).
- **Interactive Depth:** On hover, cards should subtly lift by increasing shadow spread and shifting -2px on the Y-axis.

## Shapes
The shape language is purposefully **Rounded**, creating a friendly and modern interface. 

- **Standard Elements (Buttons, Inputs):** 0.5rem (8px) radius.
- **Containers (Cards, Section Wrappers):** 1rem (16px) radius to create a distinct, modern "container" look.
- **Full-Width Mobile Elements:** Top-only 1.5rem radius for bottom sheets and drawers.

Consistent roundedness helps soften the "institutional" feel of financial data, making the Assistant feel more approachable.

## Components

### Buttons
- **Primary:** Solid #E31E24 background, White text. No border.
- **Secondary:** Transparent background, #0F172A border (1px), #0F172A text.
- **Tertiary/Ghost:** Transparent background, #334155 text, no border.
- All buttons feature a 0.5rem corner radius and height scales of 40px (sm), 48px (md), and 56px (lg).

### Input Fields
- Clean, minimalistic style.
- 1px border (#E2E8F0) in default state.
- On focus: Border changes to #E31E24 with a soft 2px outer glow in the same color (10% opacity).
- Labels use `label-sm` positioned above the input field.

### FAQ Cards
- White background with a 1rem corner radius.
- 1px #F1F5F9 border.
- Use a soft shadow on hover to indicate interactivity.
- Internal padding: 24px (1.5rem).

### Chips & Tags
- Used for categories (e.g., "Equity," "Tax").
- Soft background tints of the primary color (e.g., 5% opacity red) with #E31E24 text.
- Pill-shaped (fully rounded corners).

### Search Bar (Assistant)
- Large, prominent input with a 1rem radius.
- Include a subtle "Magnifying Glass" icon in #94A3B8.
- Use a persistent Level 1 shadow to make it the focal point of the FAQ landing page.