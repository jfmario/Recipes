---
name: adapt-recipe
description: >-
  Takes an existing recipe in this repo and produces a new markdown recipe that
  applies requested adaptations.
disable-model-invocation: true
---

# Adapt Recipe

The task is to read an existing recipe from this project, apply adaptations, and write a new markdown file that follows the same standards as new recipes.

## Input

The user must provide the following. Ask if they do not.

- Recipe Name
- Recipe Location
- Source Recipe: Existing recipe within the project.
- Adaptations: Concrete changes to make.

## Instructions

- Write a new recipe based on the old one.
- Make the changes necessary to implement the adaptations. 
- Conduct research if necessary on how the adaptations might require other changes.
- Consult the `new-recipe` skill for guidance on recipe tone and standards.
- Write the output file including frontmatter. All tags should be re-evaluated.

## Tag Definitions

Apply in frontmatter when applicable (same meanings as `new-recipe`):

- `vegan`: Vegan
- `vegetarian`: Vegetarian
- `lenten`: No meat, fish, eggs, or dairy. Invertebrates such as shrimp are OK.
- `lenten-light`: As lenten, except dairy and eggs are allowed.
- `gluten-free`: Contains no gluten.
- `gluten-light`: Contains minimal gluten, or gluten is avoidable by an eater. Some soy sauce or similar is okay.
