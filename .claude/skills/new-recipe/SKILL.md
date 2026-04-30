---
name: new-recipe
description: Re-write a recipe into our standards.
disable-model-invocation: true
---

# New Recipe

The task is read a recipe, normalize to 8 servings and adjust it according to our standards, and write a markdown file.

## Input

The user must provide the following. Ask if they do not.

- Recipe Name
- Recipe: The recipe will either be an attached file (such as a PDF) or the URL to a recipe on the web.

The user may provide the following.

- Adjustments: Any adjustments to make to the recipe.

## Instructions

- Understand the recipe. 
- Scale the recipe to 8 servings. Round all measurements to a sane kitchen measurements (ie, 3.1 cloves of garlic becomes 3, and 1.42 cups becomes 1.5 cups). Aromatics should round up, everything else can round to the nearest.
- The recipe is to be re-written in an authoritative and instructional tone rather than copying original prose.
- Ingredients should be listed in a single flat list in a logical order, with no subsections or groupings. Water and other universally assumed pantry staples do not need to be listed. Small amounts of non-main ingredients (such as spices, salt, pepper, or a splash of oil) do not need to appear in the ingredients list — they will be introduced inline during the steps when needed.
- Every step must include the specific amounts needed right in the instruction text (e.g., "Add 1 tsp cumin and 1/2 tsp smoked paprika"). The cook should never need to scroll back to the ingredients list while working.
- Write all fractions using plain text (e.g., 1/2, 3/4, 2/3, 1 1/2). Never use special Unicode fraction characters (½, ¾, ⅔, etc.).
- Include preparation and "hidden" steps such as pre-heating ovens or dicing onions at the right time. We don't want to need chopped onion and not have it chopped yet, or need to make many spice measurements when time is of the essence. Make no assumptions about an onion being already diced.
- Write a markdown file based on the template in `references/recipe-template.md`.
- Decide on tags to include in the frontmatter. Consider each one below.

## Tag Definitions

These tags should be applied in the frontmatter if applicable.

- `vegan`: Vegan
- `vegetarian`: Vegetarian
- `lenten`: No meat, fish, eggs, or dairy. Invertebrates such as shrimp are OK.
- `lenten-light`: As lenten, except dairy and eggs are allowed.
- `gluten-free`: Contains no gluten.
- `gluten-light`: Contains minimal gluten, or gluten is avoidable by an eater. Some soy sauce or similar is okay.
