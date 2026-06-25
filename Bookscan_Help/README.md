# Bookscan Help Files

Reference material from Bookscan's built-in help system (Help & Manual export), used for cross-referencing documented behaviour against what our sync actually does.

## Layout

- `*.htm` — individual help topic pages (export from Bookscan's help viewer)
- `images/` — embedded screenshots / diagrams referenced by the help pages

## Primary use cases

- **Phase 3 upstream investigation** — answering "how does Bookscan receive bibliographic updates from Nielsen BookData / TitlePage?"
- **Operational reference** — verifying Bookscan workflows Louisa describes (e-Comms config, EDI, web orders, inventory)
- **Documenting the integration** — quoting Bookscan's documented behaviour in the BookKeeper docs (`bookkeeper_docs/`) where relevant

## Source

Built with **Help & Manual** software (per the `<meta name="generator">` tag in the rendered HTML). Each topic is a standalone `.htm` file with relative image references — exports cleanly if you save the whole tree together.
