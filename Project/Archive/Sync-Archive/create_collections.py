"""
BMBooks — Create Shopify smart collections with SEO copy.

Creates:
  - 7 top-nav parent collections (tag-driven from Bookscan MAINCAT)
  - New Releases, Bestsellers, Forthcoming Titles (Bookscan-driven)
  - Sub-collections for Fiction, Kids, Non-Fiction, The Arts,
    New Zealand, Gifts & Stationery, History & Politics, Well Being,
    Sciences, Travel, Biographies, Sport, The Garden (from Bookscan SUBCAT tags)

Staff Picks and NZ Authors are NOT created here — Louisa curates those
manually in Shopify Admin as custom collections.

Run once. Safe to re-run — skips any collection whose handle already exists.

Sub-collection tag values are exact Bookscan SUBCAT names as applied by
bookscan_sync.py. Do not change without updating the sync script too.

Usage:
    python create_collections.py
"""

import os
import requests

SHOPIFY_STORE_URL    = os.environ.get("SHOPIFY_STORE_URL", "bruce-mckenzie-booksellers.myshopify.com")
SHOPIFY_ACCESS_TOKEN = os.environ["SHOPIFY_ACCESS_TOKEN"]

BASE_URL = f"https://{SHOPIFY_STORE_URL}/admin/api/2024-01"
HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
}


def tag(value):
    return {"column": "tag", "relation": "equals", "condition": value}


COLLECTIONS = [
    # ── Top nav (7) ──────────────────────────────────────────────────────────
    {
        "title": "Fiction",
        "handle": "fiction",
        "seo_title": "Fiction Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Browse fiction books in NZ at Bruce McKenzie Booksellers. Literary fiction, crime, romance, fantasy and more — chosen by our expert team.",
        "body_html": "Lose yourself in a great story. Our fiction collection spans literary fiction, crime and thriller, romance, fantasy, science fiction, and everything in between. Chosen by our team of passionate readers in Palmerston North.",
        "disjunctive": False,
        "rules": [tag("Fiction")],
    },
    {
        "title": "Young Adult",
        "handle": "young-adult",
        "seo_title": "Young Adult Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop young adult books in NZ at Bruce McKenzie Booksellers. Fiction, fantasy, contemporary YA and more for teenage readers.",
        "body_html": "Books for teenage readers and beyond — from coming-of-age stories to fantasy epics. Our young adult collection is personally chosen by the team at Bruce McKenzie Booksellers, Palmerston North.",
        "disjunctive": False,
        "rules": [tag("Teen Fiction")],
    },
    {
        "title": "Kids",
        "handle": "kids",
        "seo_title": "Children's Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop children's books in NZ at Bruce McKenzie Booksellers. Picture books, junior fiction, young adult and more — expertly chosen for NZ kids.",
        "body_html": "A carefully chosen collection of children's books for every age and stage. From picture books for little ones to junior fiction for older readers, our team handpicks titles that NZ kids will love. Find us in Palmerston North or shop online.",
        "disjunctive": False,
        "rules": [tag("Children")],
    },
    {
        "title": "Non-Fiction",
        "handle": "non-fiction",
        "seo_title": "Non-Fiction Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Browse non-fiction books in NZ at Bruce McKenzie Booksellers. History, biography, science, cooking, self-help and more — in store and online.",
        "body_html": "Explore the world through non-fiction. From history and biography to cooking, science, and self-help, our non-fiction collection covers every curiosity. Browse in store at 37 George Street or shop online.",
        "disjunctive": True,
        "rules": [
            tag("History And Politics"),
            tag("Sciences"),
            tag("Biographies"),
            tag("Well Being"),
            tag("Travel"),
            tag("Reference"),
            tag("Sport"),
            tag("The Garden"),
            tag("Motoring"),
            tag("Audio"),
        ],
    },
    {
        "title": "The Arts",
        "handle": "the-arts",
        "seo_title": "Art Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Browse art, craft, photography, architecture and design books in NZ at Bruce McKenzie Booksellers. In store in Palmerston North and online.",
        "body_html": "Books on art, craft, photography, architecture, design, fashion, and music. A rich collection for creators and art lovers, chosen by our team at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("The Arts")],
    },
    {
        "title": "New Zealand",
        "handle": "new-zealand",
        "seo_title": "New Zealand Books | Bruce McKenzie Booksellers",
        "seo_description": "Shop New Zealand books at Bruce McKenzie Booksellers. NZ fiction, history, biography, Māori, art and more — in store in Palmerston North and online.",
        "body_html": "Celebrating the best of Aotearoa New Zealand — fiction, history, biography, art, and culture from NZ writers and about NZ subjects. A proud showcase of our local identity, from the team at Bruce McKenzie Booksellers, Palmerston North.",
        "disjunctive": True,
        "rules": [
            tag("Te Ao Maori"),
            tag("The Manawatu"),
            tag("Maori Language"),
            tag("Maori Studies and History"),
            tag("Maori Picture Books"),
            tag("Maori Art"),
            tag("NZ Fiction"),
            tag("NZ History"),
            tag("NZ Military"),
            tag("NZ Sciences"),
            tag("NZ Environment"),
            tag("NZ Art"),
            tag("NZ Gardening"),
            tag("NZ Sociology"),
            tag("New Zealand Biography"),
            tag("New Zealand Picture Books"),
            tag("New Zealand Travel"),
            tag("Books About Palmy"),
            tag("Our Authors"),
        ],
    },
    {
        "title": "Gifts & Stationery",
        "handle": "gifts-stationery",
        "seo_title": "Gifts & Stationery | Bruce McKenzie Booksellers",
        "seo_description": "Shop gifts, stationery, games and puzzles at Bruce McKenzie Booksellers in Palmerston North. Great gifts for book lovers, in store and online.",
        "body_html": "Browse our collection of gifts, stationery, games, puzzles, and calendars. The perfect finishing touch alongside a great book — available in store at Bruce McKenzie Booksellers, Palmerston North.",
        "disjunctive": False,
        "rules": [tag("Stationery Puzzles And Gifts")],
    },
    # ── Editorial / Bookscan-driven ──────────────────────────────────────────
    {
        "title": "New Releases",
        "handle": "new-releases",
        "seo_title": "New Releases | Bruce McKenzie Booksellers",
        "seo_description": "Shop the latest book releases in NZ at Bruce McKenzie Booksellers. New fiction, non-fiction, children's and more — updated regularly.",
        "body_html": "Stay up to date with the latest books from around the world. Our new releases collection is updated regularly with the titles everyone's talking about — available in store in Palmerston North and online across New Zealand.",
        "disjunctive": False,
        "rules": [tag("New Arrivals")],
    },
    {
        "title": "Bestsellers",
        "handle": "bestsellers",
        "seo_title": "Bestselling Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop bestselling books in NZ at Bruce McKenzie Booksellers. The most popular titles right now — fiction, non-fiction, children's and more.",
        "body_html": "The most loved books right now. Our bestsellers collection brings together the titles NZ readers are buying most — from chart-topping fiction to must-read non-fiction. Updated regularly to keep you in the loop.",
        "disjunctive": False,
        "rules": [tag("Bestsellers")],
    },
    {
        "title": "Forthcoming Titles",
        "handle": "forthcoming-titles",
        "seo_title": "Forthcoming Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Pre-order forthcoming books at Bruce McKenzie Booksellers. Secure your copy of the most anticipated new releases in NZ.",
        "body_html": "Be the first to know about upcoming releases. Browse and pre-order the most anticipated forthcoming titles — secured and ready to ship as soon as they arrive at Bruce McKenzie Booksellers, Palmerston North.",
        "disjunctive": False,
        "rules": [tag("Forthcoming")],
    },

    # ── Fiction sub-collections ───────────────────────────────────────────────
    {
        "title": "General Fiction",
        "handle": "general-fiction",
        "seo_title": "General Fiction Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Browse general fiction books in NZ at Bruce McKenzie Booksellers. Contemporary novels, literary fiction and more from our expert team.",
        "body_html": "From debut novels to established favourites, our general fiction collection covers the full breadth of contemporary and literary fiction. Handpicked by the team at Bruce McKenzie Booksellers, Palmerston North.",
        "disjunctive": False,
        "rules": [tag("General Fiction")],
    },
    {
        "title": "Classics",
        "handle": "classics",
        "seo_title": "Classic Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop classic literature in NZ at Bruce McKenzie Booksellers. Timeless novels and essential reads — in store in Palmerston North and online.",
        "body_html": "The books that have shaped literature — from Victorian novels to twentieth-century masterworks. Our classics collection brings together the essential reads every bookshelf deserves, available at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Classics")],
    },
    {
        "title": "Crime Fiction",
        "handle": "crime-fiction",
        "seo_title": "Crime Fiction Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop crime fiction books in NZ at Bruce McKenzie Booksellers. Thrillers, detective fiction, mysteries and more — in store in Palmerston North.",
        "body_html": "Page-turning crime fiction from the best writers in the genre. From classic detective novels to modern psychological thrillers, our crime collection has your next unputdownable read. Browse in store in Palmerston North or shop online.",
        "disjunctive": False,
        "rules": [tag("Crime Fiction")],
    },
    {
        "title": "Science Fiction & Fantasy",
        "handle": "science-fiction-and-fantasy",
        "seo_title": "Science Fiction & Fantasy Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop science fiction and fantasy books in NZ at Bruce McKenzie Booksellers. Epic fantasy, sci-fi, speculative fiction and more.",
        "body_html": "Journey beyond the boundaries of the known world. Our science fiction and fantasy collection spans epic fantasy series, hard science fiction, speculative fiction, and everything in between — curated by our team of passionate readers.",
        "disjunctive": False,
        "rules": [tag("Science Fiction and Fantasy")],
    },
    {
        "title": "Graphic Novels",
        "handle": "graphic-novels",
        "seo_title": "Graphic Novels NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop graphic novels and comics in NZ at Bruce McKenzie Booksellers. Manga, superhero, literary graphic novels and more.",
        "body_html": "Stories told through sequential art. Our graphic novel collection covers literary graphic novels, manga, superhero comics, and independent titles — a vibrant range for readers of all ages at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Graphic Novels")],
    },
    {
        "title": "Poetry",
        "handle": "poetry",
        "seo_title": "Poetry Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop poetry books in NZ at Bruce McKenzie Booksellers. New Zealand and international poets, classic and contemporary collections.",
        "body_html": "Poetry collections from New Zealand and around the world — classic voices, contemporary poets, and debut collections. A carefully curated range for poetry lovers at Bruce McKenzie Booksellers, Palmerston North.",
        "disjunctive": False,
        "rules": [tag("Poetry")],
    },
    {
        "title": "NZ Fiction",
        "handle": "nz-fiction",
        "seo_title": "NZ Fiction Books | Bruce McKenzie Booksellers",
        "seo_description": "Shop New Zealand fiction at Bruce McKenzie Booksellers. Novels and short stories by NZ authors — in store in Palmerston North and online.",
        "body_html": "Fiction by New Zealand writers — from award-winning literary novels to gripping crime and compelling debuts. Proudly championing local voices at Bruce McKenzie Booksellers, Palmerston North.",
        "disjunctive": False,
        "rules": [tag("NZ Fiction")],
    },
    {
        "title": "Historical Fiction",
        "handle": "historical-fiction",
        "seo_title": "Historical Fiction Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop historical fiction in NZ at Bruce McKenzie Booksellers. Novels set across different eras and places — in store and online.",
        "body_html": "Travel through time with our historical fiction collection. From ancient civilisations to the twentieth century, these novels bring the past to life — meticulously researched and brilliantly told. Available at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Historical Fiction")],
    },
    {
        "title": "Plays",
        "handle": "plays",
        "seo_title": "Plays & Drama Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop plays and drama scripts in NZ at Bruce McKenzie Booksellers. Classic and contemporary theatre from NZ and international playwrights.",
        "body_html": "Scripts and plays from classic and contemporary theatre — Shakespeare to modern NZ playwrights. A specialist range for theatre lovers and students at Bruce McKenzie Booksellers, Palmerston North.",
        "disjunctive": False,
        "rules": [tag("Plays")],
    },

    # ── Kids sub-collections ──────────────────────────────────────────────────
    {
        "title": "Children's Fiction",
        "handle": "childrens-fiction",
        "seo_title": "Children's Fiction NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop children's fiction in NZ at Bruce McKenzie Booksellers. Chapter books, junior novels and middle grade fiction for NZ kids.",
        "body_html": "Adventure, mystery, friendship, and imagination — our children's fiction collection has chapter books and junior novels for every kind of young reader. Chosen with care by the team at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Childrens Fiction")],
    },
    {
        "title": "Picture Books",
        "handle": "picture-books",
        "seo_title": "Children's Picture Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop children's picture books in NZ at Bruce McKenzie Booksellers. Beautiful picture books for babies, toddlers and early readers.",
        "body_html": "Beautifully illustrated picture books for babies, toddlers, and early readers. Our picture book collection is chosen by our team to spark imagination and a love of reading from the very first page — available at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Childrens Picture Books")],
    },
    {
        "title": "NZ Picture Books",
        "handle": "nz-picture-books",
        "seo_title": "NZ Picture Books | Bruce McKenzie Booksellers",
        "seo_description": "Shop New Zealand picture books at Bruce McKenzie Booksellers. Stories set in Aotearoa for young readers — in store in Palmerston North.",
        "body_html": "Picture books set in Aotearoa and written by New Zealand authors and illustrators. Celebrate local stories and scenery with our range of NZ picture books — a wonderful way to connect young readers with their home.",
        "disjunctive": False,
        "rules": [tag("New Zealand Picture Books")],
    },
    {
        "title": "Children's Non-Fiction",
        "handle": "childrens-non-fiction",
        "seo_title": "Children's Non-Fiction NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop children's non-fiction books in NZ at Bruce McKenzie Booksellers. Educational and activity books for curious young readers.",
        "body_html": "Feed young curiosity with our children's non-fiction collection — books about animals, nature, science, history, and the world around us. Engaging and educational reads for children of all ages at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Childrens Non Fiction")],
    },
    {
        "title": "Books for Babies",
        "handle": "books-for-babies",
        "seo_title": "Baby Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop baby and toddler books in NZ at Bruce McKenzie Booksellers. Board books, cloth books and first stories for babies and toddlers.",
        "body_html": "Soft, tactile, and full of wonder — our baby book collection includes board books, cloth books, and gentle first stories perfect for reading aloud. Start your little one's reading journey at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Books For Babies")],
    },
    {
        "title": "Activity Books",
        "handle": "activity-books",
        "seo_title": "Children's Activity Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop children's activity books in NZ at Bruce McKenzie Booksellers. Colouring, puzzle, craft and activity books for kids.",
        "body_html": "Keep young hands and minds busy with our activity book collection — colouring books, puzzle books, dot-to-dot, craft activities, and more. Great for rainy days and screen-free fun, available at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Activities")],
    },
    {
        "title": "Study & Education",
        "handle": "study-and-education",
        "seo_title": "Study & Education Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop study and education books in NZ at Bruce McKenzie Booksellers. School resources, study guides and educational books for NZ students.",
        "body_html": "Study guides, school resources, and educational titles for New Zealand students. Whether preparing for exams or building foundational skills, our study and education range supports learners at every level.",
        "disjunctive": False,
        "rules": [tag("Study And Education")],
    },

    # ── Non-Fiction sub-collections (MAINCAT level) ───────────────────────────
    {
        "title": "Health & Wellbeing",
        "handle": "health-and-wellbeing",
        "seo_title": "Health & Wellbeing Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop health and wellbeing books in NZ at Bruce McKenzie Booksellers. Nutrition, psychology, self-help, mindfulness and more.",
        "body_html": "Books to nourish body and mind — from nutrition and fitness to psychology, mindfulness, and self-help. Our health and wellbeing collection covers every aspect of living well, chosen by the team at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Well Being")],
    },
    {
        "title": "History & Politics",
        "handle": "history-and-politics",
        "seo_title": "History & Politics Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop history and politics books in NZ at Bruce McKenzie Booksellers. World history, NZ history, political science and more.",
        "body_html": "Understand the world through history and politics. From ancient civilisations to modern geopolitics, our collection spans world history, New Zealand history, political biography, and current affairs — available at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("History And Politics")],
    },
    {
        "title": "Science & Nature",
        "handle": "science-and-nature",
        "seo_title": "Science & Nature Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop science and nature books in NZ at Bruce McKenzie Booksellers. Environment, biology, physics, popular science and more.",
        "body_html": "Explore the natural world and the frontiers of human knowledge. Our science and nature collection covers popular science, environment, biology, physics, and the big questions facing our planet — at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Sciences")],
    },
    {
        "title": "Travel",
        "handle": "travel",
        "seo_title": "Travel Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop travel books in NZ at Bruce McKenzie Booksellers. Travel guides, travel memoirs, maps and language books for every destination.",
        "body_html": "Plan your next adventure or travel from the armchair. Our travel collection includes destination guides, travel memoirs, maps, atlases, and language books — everything for the curious traveller at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Travel")],
    },
    {
        "title": "Biographies",
        "handle": "biographies",
        "seo_title": "Biography Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop biography and memoir books in NZ at Bruce McKenzie Booksellers. Life stories from fascinating people — in store and online.",
        "body_html": "Life stories that inspire, challenge, and illuminate. Our biography and memoir collection covers political leaders, artists, athletes, and everyday people — New Zealand voices and international figures, all at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Biographies")],
    },
    {
        "title": "Sport",
        "handle": "sport",
        "seo_title": "Sport Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop sport books in NZ at Bruce McKenzie Booksellers. Rugby, cycling, cricket, fitness and more — in store in Palmerston North.",
        "body_html": "Books for sports lovers — from rugby and cricket to cycling, fitness, and the great sporting stories of our time. Our sport collection celebrates the passion and dedication behind the games we love, at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Sport")],
    },
    {
        "title": "The Garden",
        "handle": "the-garden",
        "seo_title": "Gardening Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop gardening books in NZ at Bruce McKenzie Booksellers. NZ gardening guides, plant books, and garden design inspiration.",
        "body_html": "Everything for the NZ gardener — from practical growing guides and plant identification to garden design and the philosophy of a life outdoors. Our gardening collection is chosen for New Zealand conditions and climates.",
        "disjunctive": False,
        "rules": [tag("The Garden")],
    },
    {
        "title": "Food & Drink",
        "handle": "food-and-drink",
        "seo_title": "Food & Drink Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop food and drink books in NZ at Bruce McKenzie Booksellers. Cookbooks, wine, baking, and food culture from NZ and around the world.",
        "body_html": "From everyday cooking to ambitious weekend projects — our food and drink collection covers cookbooks, baking, wine, and food culture from New Zealand and around the world. Find your next favourite cookbook at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Food And Beverage")],
    },

    # ── The Arts sub-collections ──────────────────────────────────────────────
    {
        "title": "Art Books",
        "handle": "art-books",
        "seo_title": "Art Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop art books in NZ at Bruce McKenzie Booksellers. Fine art, art history, NZ art and artist monographs — in store and online.",
        "body_html": "Celebrate the visual arts with our art book collection — artist monographs, art history, gallery catalogues, and NZ art. A rich range for collectors, students, and art lovers at Bruce McKenzie Booksellers, Palmerston North.",
        "disjunctive": False,
        "rules": [tag("Art")],
    },
    {
        "title": "Craft",
        "handle": "craft",
        "seo_title": "Craft Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop craft books in NZ at Bruce McKenzie Booksellers. Knitting, sewing, quilting, paper craft and more — in store and online.",
        "body_html": "Inspire your next creative project with our craft book collection. From knitting and sewing to paper craft and mixed media — practical, beautiful, and full of ideas for makers of every skill level at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Craft")],
    },
    {
        "title": "Music & Performing Arts",
        "handle": "music-and-performing-arts",
        "seo_title": "Music & Performing Arts Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop music and performing arts books in NZ at Bruce McKenzie Booksellers. Music history, film, theatre and dance books.",
        "body_html": "Books on music, film, theatre, and dance — from artist biographies and music history to screenwriting and the business of performance. Our performing arts collection celebrates the full spectrum of creative expression.",
        "disjunctive": False,
        "rules": [tag("Music And Performing Arts")],
    },
    {
        "title": "Fashion",
        "handle": "fashion",
        "seo_title": "Fashion Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop fashion books in NZ at Bruce McKenzie Booksellers. Fashion history, designer monographs, style guides and more.",
        "body_html": "Explore the world of fashion through our curated collection — designer monographs, fashion history, styling guides, and the cultural stories behind the clothes we wear. Available at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Fashion")],
    },
    {
        "title": "Design",
        "handle": "design",
        "seo_title": "Design Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop design books in NZ at Bruce McKenzie Booksellers. Graphic design, interior design, product design and architecture books.",
        "body_html": "Books on graphic design, interior design, industrial design, and the creative process. Our design collection is a resource for professionals, students, and anyone who appreciates thoughtful, purposeful creativity.",
        "disjunctive": False,
        "rules": [tag("Design")],
    },
    {
        "title": "Photography",
        "handle": "photography",
        "seo_title": "Photography Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop photography books in NZ at Bruce McKenzie Booksellers. Photo books, technique guides and photographer monographs.",
        "body_html": "Stunning photography books — from technique guides and camera manuals to photographer monographs and large-format photo books documenting the world's most compelling places and people. Available at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Photography")],
    },
    {
        "title": "Architecture",
        "handle": "architecture",
        "seo_title": "Architecture Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop architecture books in NZ at Bruce McKenzie Booksellers. Architectural history, design, NZ architecture and more.",
        "body_html": "From architectural history and theory to stunning monographs on individual buildings and designers — our architecture collection is a rich resource for professionals, students, and admirers of the built environment.",
        "disjunctive": False,
        "rules": [tag("Architecture")],
    },

    # ── New Zealand sub-collections ───────────────────────────────────────────
    {
        "title": "Māori Studies & History",
        "handle": "maori-studies-and-history",
        "seo_title": "Māori Studies & History Books | Bruce McKenzie Booksellers",
        "seo_description": "Shop Māori studies and history books at Bruce McKenzie Booksellers. Te ao Māori, NZ history, and tikanga books in store and online.",
        "body_html": "Books exploring Māori history, tikanga, whakapapa, and the broader story of Te Ao Māori. A thoughtfully chosen collection celebrating and preserving the knowledge and culture of tangata whenua, at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Maori Studies and History")],
    },
    {
        "title": "Māori Picture Books",
        "handle": "maori-picture-books",
        "seo_title": "Māori Picture Books | Bruce McKenzie Booksellers",
        "seo_description": "Shop Māori picture books at Bruce McKenzie Booksellers. Te reo Māori and bilingual picture books for tamariki — in store and online.",
        "body_html": "Bilingual and te reo Māori picture books for tamariki of all ages. Our Māori picture book collection nurtures language and cultural connection from the very earliest years — available at Bruce McKenzie Booksellers, Palmerston North.",
        "disjunctive": False,
        "rules": [tag("Maori Picture Books")],
    },
    {
        "title": "Te Reo Māori",
        "handle": "te-reo-maori",
        "seo_title": "Te Reo Māori Books | Bruce McKenzie Booksellers",
        "seo_description": "Shop te reo Māori books at Bruce McKenzie Booksellers. Language learning, dictionaries and te reo resources in store and online.",
        "body_html": "Resources for learning and celebrating te reo Māori — dictionaries, language guides, graded readers, and books supporting the revitalisation of our national language. Available at Bruce McKenzie Booksellers, Palmerston North.",
        "disjunctive": False,
        "rules": [tag("Maori Language")],
    },
    {
        "title": "NZ History",
        "handle": "nz-history",
        "seo_title": "New Zealand History Books | Bruce McKenzie Booksellers",
        "seo_description": "Shop New Zealand history books at Bruce McKenzie Booksellers. NZ colonial history, ANZAC, Māori history and more — in store and online.",
        "body_html": "The story of Aotearoa New Zealand — from pre-European settlement and colonisation to the world wars and modern politics. Our NZ history collection is essential reading for anyone who wants to understand this place we call home.",
        "disjunctive": False,
        "rules": [tag("NZ History")],
    },
    {
        "title": "Our Authors — Manawatū",
        "handle": "manawatu-authors",
        "seo_title": "Manawatū Authors | Bruce McKenzie Booksellers",
        "seo_description": "Books by Manawatū and Palmerston North authors at Bruce McKenzie Booksellers. Proudly supporting our local writing community.",
        "body_html": "Proudly celebrating the writers of Manawatū and Palmerston North. From debut novelists to established local voices, our Manawatū authors collection is a showcase of the talent on our doorstep — available exclusively at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Our Authors")],
    },
    {
        "title": "Books About Palmy",
        "handle": "books-about-palmy",
        "seo_title": "Books About Palmerston North | Bruce McKenzie Booksellers",
        "seo_description": "Shop books about Palmerston North and the Manawatū at Bruce McKenzie Booksellers. Local history, guides and stories about our city.",
        "body_html": "Books about Palmerston North and the Manawatū region — local history, guides, photography, and stories about the city and people we know and love. A unique collection available at Bruce McKenzie Booksellers, 37 George Street.",
        "disjunctive": False,
        "rules": [tag("Books About Palmy")],
    },

    # ── Gifts & Stationery sub-collections ───────────────────────────────────
    {
        "title": "Stationery",
        "handle": "stationery",
        "seo_title": "Stationery NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop stationery at Bruce McKenzie Booksellers in Palmerston North. Notebooks, journals, pens, cards and more — in store and online.",
        "body_html": "Beautiful stationery for writing, planning, and gifting. Notebooks, journals, greeting cards, wrapping paper, and writing accessories — a carefully chosen range for people who love beautiful things at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Stationery")],
    },
    {
        "title": "Games & Puzzles",
        "handle": "games-and-puzzles",
        "seo_title": "Games & Puzzles NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop games and puzzles in NZ at Bruce McKenzie Booksellers. Board games, jigsaw puzzles, card games and more — great gifts.",
        "body_html": "Screen-free fun for the whole family. Our games and puzzles collection includes board games, jigsaw puzzles, card games, and word games — perfect gifts for birthdays, Christmas, and any occasion at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Games and Puzzles")],
    },
    {
        "title": "Gifts",
        "handle": "gifts",
        "seo_title": "Book Gifts NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop gifts for book lovers in NZ at Bruce McKenzie Booksellers. Unique gifts, bookish accessories and more — in store in Palmerston North.",
        "body_html": "The perfect gift for the book lover in your life. Browse our curated range of bookish gifts, accessories, and unique items alongside a hand-picked book recommendation from the team at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Gifts")],
    },
    {
        "title": "Calendars & Diaries",
        "handle": "calendars-and-diaries",
        "seo_title": "Calendars & Diaries NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop calendars and diaries in NZ at Bruce McKenzie Booksellers. Wall calendars, desk calendars, day planners and diaries.",
        "body_html": "Plan your year in style with our range of calendars, desk diaries, and day planners. From art calendars to practical organisers, our range covers every taste and need — available at Bruce McKenzie Booksellers, Palmerston North.",
        "disjunctive": False,
        "rules": [tag("Calendars And Diaries")],
    },

    # ── History & Politics sub-collections ───────────────────────────────────
    {
        "title": "History",
        "handle": "history",
        "seo_title": "History Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop history books in NZ at Bruce McKenzie Booksellers. World history, ancient civilisations, military history and more — in store and online.",
        "body_html": "From ancient civilisations and the great empires to the world wars and modern geopolitics — our history collection spans every era and corner of the globe. Chosen by our team of passionate readers at Bruce McKenzie Booksellers, Palmerston North.",
        "disjunctive": False,
        "rules": [tag("History")],
    },
    {
        "title": "Politics",
        "handle": "politics",
        "seo_title": "Politics Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop politics books in NZ at Bruce McKenzie Booksellers. Political history, current affairs, political theory and biography — in store and online.",
        "body_html": "Understand power, ideology, and the forces that shape our world. Our politics collection covers political history, current affairs, political biography, and theory — from local NZ politics to global movements, at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Politics")],
    },
    {
        "title": "Religion & Spirituality",
        "handle": "religion",
        "seo_title": "Religion & Spirituality Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop religion and spirituality books in NZ at Bruce McKenzie Booksellers. World religions, theology, scripture and spiritual practice — in store and online.",
        "body_html": "Explore the world's great religious traditions and spiritual practices. Our religion collection covers theology, scripture, world religions, and contemplative practice — a thoughtful range for seekers and students at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Religion")],
    },
    {
        "title": "Mythology",
        "handle": "mythology",
        "seo_title": "Mythology Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop mythology books in NZ at Bruce McKenzie Booksellers. Greek, Norse, world mythology and folklore — in store in Palmerston North and online.",
        "body_html": "The great myths and legends of human civilisation — Greek, Roman, Norse, Celtic, and Māori. Our mythology collection brings together the stories that shaped cultures across the world, available at Bruce McKenzie Booksellers, Palmerston North.",
        "disjunctive": False,
        "rules": [tag("Mythology")],
    },
    {
        "title": "True Crime",
        "handle": "true-crime",
        "seo_title": "True Crime Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop true crime books in NZ at Bruce McKenzie Booksellers. Real crime investigations, criminal biography and forensic narratives — in store and online.",
        "body_html": "Gripping real-world investigations, criminal biographies, and forensic narratives that read like fiction. Our true crime collection covers the most compelling cases from New Zealand and around the world, at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("True Crime")],
    },

    # ── Well Being sub-collections ────────────────────────────────────────────
    {
        "title": "Psychology",
        "handle": "psychology",
        "seo_title": "Psychology Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop psychology books in NZ at Bruce McKenzie Booksellers. Popular psychology, cognitive science, mental health and self-help — in store and online.",
        "body_html": "Understand how the mind works with our popular psychology collection — from cognitive science and behavioural psychology to mental health, self-help, and the latest in neuroscience. Thoughtfully chosen by the team at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Psychology")],
    },
    {
        "title": "Health",
        "handle": "health",
        "seo_title": "Health Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop health books in NZ at Bruce McKenzie Booksellers. Nutrition, fitness, medical guides, and healthy living — in store in Palmerston North and online.",
        "body_html": "Books to help you live well — nutrition guides, fitness resources, medical references, and practical health advice. Our health collection is chosen to support every aspect of your wellbeing at Bruce McKenzie Booksellers, Palmerston North.",
        "disjunctive": False,
        "rules": [tag("Health")],
    },
    {
        "title": "New Age & Spirituality",
        "handle": "new-age",
        "seo_title": "New Age & Spiritual Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop new age and spiritual books in NZ at Bruce McKenzie Booksellers. Astrology, tarot, crystals, mindfulness and more — in store and online.",
        "body_html": "Explore the metaphysical, the spiritual, and the esoteric with our new age collection — astrology, tarot, crystals, energy healing, and mindfulness. A wide-ranging selection for the spiritually curious at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("New Age")],
    },
    {
        "title": "Children's Wellbeing",
        "handle": "childrens-wellbeing",
        "seo_title": "Children's Wellbeing Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop children's wellbeing books in NZ at Bruce McKenzie Booksellers. Books on emotions, mental health, and resilience for kids — in store and online.",
        "body_html": "Books that help children understand their feelings, build resilience, and navigate life's challenges. Our children's wellbeing collection supports emotional development and mental health for kids of every age, chosen by the team at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Childrens Well Being")],
    },
    {
        "title": "Gender & Identity",
        "handle": "gender",
        "seo_title": "Gender & Identity Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop gender and identity books in NZ at Bruce McKenzie Booksellers. Gender studies, feminism, LGBTQ+ and identity — in store and online.",
        "body_html": "Books exploring gender, identity, feminism, and LGBTQ+ experience — from academic texts to personal memoirs and cultural criticism. A diverse and thoughtful collection for every reader at Bruce McKenzie Booksellers, Palmerston North.",
        "disjunctive": False,
        "rules": [tag("Gender")],
    },
    {
        "title": "Family & Parenting",
        "handle": "family",
        "seo_title": "Family & Parenting Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop family and parenting books in NZ at Bruce McKenzie Booksellers. Parenting guides, pregnancy, relationships and family life — in store and online.",
        "body_html": "Practical and inspiring books on parenting, relationships, and family life — from pregnancy and early childhood to navigating the teenage years. Our family collection offers support and insight at every stage at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Family")],
    },
    {
        "title": "Humour",
        "handle": "humour",
        "seo_title": "Humour Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop humour books in NZ at Bruce McKenzie Booksellers. Funny books, comedy memoirs, satire and more — great gifts in store and online.",
        "body_html": "Books that make you laugh out loud — from sharp satire and comic novels to laugh-a-minute memoirs and absurdist fiction. Our humour collection is a guaranteed mood lift and makes a brilliant gift, available at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Humour")],
    },

    # ── Sciences sub-collections ──────────────────────────────────────────────
    {
        "title": "Environment",
        "handle": "environment",
        "seo_title": "Environment Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop environment and ecology books in NZ at Bruce McKenzie Booksellers. Climate change, conservation, nature writing and more — in store and online.",
        "body_html": "Essential reading for our times — books on climate change, conservation, ecology, and the natural world. Our environment collection spans scientific analysis to nature writing that inspires action at Bruce McKenzie Booksellers, Palmerston North.",
        "disjunctive": False,
        "rules": [tag("Environment")],
    },
    {
        "title": "Popular Science",
        "handle": "general-science",
        "seo_title": "Popular Science Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop popular science books in NZ at Bruce McKenzie Booksellers. Physics, biology, mathematics, astronomy and more — in store and online.",
        "body_html": "Accessible, fascinating popular science from the world's best science writers — physics, biology, mathematics, astronomy, and the big questions about life, the universe, and everything. At Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("General Science")],
    },
    {
        "title": "Business",
        "handle": "business",
        "seo_title": "Business Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop business books in NZ at Bruce McKenzie Booksellers. Management, entrepreneurship, leadership and finance — in store in Palmerston North and online.",
        "body_html": "Books for business builders, managers, and entrepreneurial minds — from strategic thinking and leadership to finance, marketing, and the stories behind the world's most successful companies, at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Business")],
    },
    {
        "title": "Philosophy",
        "handle": "philosophy",
        "seo_title": "Philosophy Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop philosophy books in NZ at Bruce McKenzie Booksellers. Ethics, metaphysics, political philosophy and popular philosophy — in store and online.",
        "body_html": "Explore the big questions of existence, ethics, knowledge, and meaning with our philosophy collection. From the ancient Greeks to contemporary thinkers — accessible popular philosophy alongside rigorous academic texts at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Philosophy")],
    },
    {
        "title": "Economics",
        "handle": "economics",
        "seo_title": "Economics Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop economics books in NZ at Bruce McKenzie Booksellers. Popular economics, economic history and business economics — in store and online.",
        "body_html": "Popular economics, economic history, and the ideas that explain how markets and societies work. Our economics collection makes complex ideas accessible — from Freakonomics to in-depth analysis of global economic trends, at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Economics")],
    },

    # ── Travel sub-collections ────────────────────────────────────────────────
    {
        "title": "Travel Writing",
        "handle": "travel-literature",
        "seo_title": "Travel Writing & Memoirs NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop travel writing and memoirs in NZ at Bruce McKenzie Booksellers. Adventure narratives and travel literature from great destinations.",
        "body_html": "Travel from your armchair with the world's greatest travel writers — vivid narratives, adventure memoirs, and literary journeys across every continent. Our travel writing collection is perfect for the curious reader at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Travel Literature")],
    },
    {
        "title": "Travel Guides",
        "handle": "travel-guides",
        "seo_title": "Travel Guides NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop travel guides in NZ at Bruce McKenzie Booksellers. Destination guides, Lonely Planet, travel phrasebooks and more — in store and online.",
        "body_html": "Plan your next adventure with our comprehensive travel guide collection — destination guides, Lonely Planet, Rough Guides, phrasebooks, and specialist travel resources for every corner of the world. Available at Bruce McKenzie Booksellers, Palmerston North.",
        "disjunctive": False,
        "rules": [tag("Travel Guides")],
    },
    {
        "title": "Language Learning",
        "handle": "languages",
        "seo_title": "Language Learning Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop language learning books in NZ at Bruce McKenzie Booksellers. Learn French, Spanish, Japanese and more — phrasebooks and language courses.",
        "body_html": "Learn a new language with our collection of phrasebooks, language courses, dictionaries, and self-study guides. From holiday essentials to deep fluency — we stock resources for dozens of languages at Bruce McKenzie Booksellers, Palmerston North.",
        "disjunctive": False,
        "rules": [tag("Languages")],
    },

    # ── Biographies sub-collection ────────────────────────────────────────────
    {
        "title": "Biography",
        "handle": "biography",
        "seo_title": "Biography Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop biography books in NZ at Bruce McKenzie Booksellers. Political, sports and arts biographies — inspiring life stories in store and online.",
        "body_html": "The lives of the remarkable, the fascinating, and the extraordinary. Our biography collection covers political leaders, artists, athletes, and everyday heroes — inspiring stories from New Zealand and around the world at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Biography")],
    },

    # ── Sport sub-collections ─────────────────────────────────────────────────
    {
        "title": "Rugby",
        "handle": "rugby",
        "seo_title": "Rugby Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop rugby books in NZ at Bruce McKenzie Booksellers. All Blacks, Rugby World Cup, player biographies and rugby history — in store and online.",
        "body_html": "Rugby runs deep in New Zealand — and our rugby collection reflects that passion. From All Blacks history and player biographies to tactical guides and Rugby World Cup retrospectives, we've got everything for the rugby fan at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Rugby")],
    },
    {
        "title": "Cycling",
        "handle": "cycling",
        "seo_title": "Cycling Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop cycling books in NZ at Bruce McKenzie Booksellers. Road cycling, mountain biking, Tour de France and cycling lifestyle — in store and online.",
        "body_html": "Books for cyclists of every kind — road racing, mountain biking, track, and the rich culture surrounding the sport. From Tour de France histories to practical training guides, our cycling collection has something for every two-wheeled enthusiast.",
        "disjunctive": False,
        "rules": [tag("Cycling")],
    },

    # ── Manawatū ──────────────────────────────────────────────────────────────
    {
        "title": "Manawatū",
        "handle": "manawatu",
        "seo_title": "Manawatū Books | Bruce McKenzie Booksellers",
        "seo_description": "Shop books by Manawatū authors and about Palmerston North at Bruce McKenzie Booksellers. Proudly supporting our local writing community.",
        "body_html": "Celebrating the stories, people, and places of Manawatū. Browse books by local authors and about Palmerston North — a collection you won't find anywhere else, available exclusively at Bruce McKenzie Booksellers, 37 George Street.",
        "disjunctive": False,
        "rules": [tag("The Manawatu")],
    },

    # ── The Garden sub-collection ─────────────────────────────────────────────
    {
        "title": "Gardening",
        "handle": "gardening",
        "seo_title": "Gardening Books NZ | Bruce McKenzie Booksellers",
        "seo_description": "Shop gardening books in NZ at Bruce McKenzie Booksellers. NZ gardening guides, vegetables, flowers, and garden design — in store and online.",
        "body_html": "Practical NZ gardening books and beautiful garden inspiration — growing vegetables, flower borders, pruning, soil care, and garden design for New Zealand's unique conditions. A rich collection for gardeners of every level at Bruce McKenzie Booksellers.",
        "disjunctive": False,
        "rules": [tag("Gardening")],
    },
]


def get_existing_handles():
    resp = requests.get(
        f"{BASE_URL}/smart_collections.json?limit=250&fields=handle",
        headers=HEADERS,
    )
    resp.raise_for_status()
    return {c["handle"] for c in resp.json()["smart_collections"]}


def create_collection(coll, existing_handles):
    if coll["handle"] in existing_handles:
        print(f"  SKIP  {coll['title']} — already exists")
        return

    payload = {
        "smart_collection": {
            "title": coll["title"],
            "handle": coll["handle"],
            "body_html": coll["body_html"],
            "disjunctive": coll["disjunctive"],
            "rules": coll["rules"],
            "metafields": [
                {
                    "namespace": "global",
                    "key": "title_tag",
                    "value": coll["seo_title"],
                    "type": "single_line_text_field",
                },
                {
                    "namespace": "global",
                    "key": "description_tag",
                    "value": coll["seo_description"],
                    "type": "single_line_text_field",
                },
            ],
        }
    }

    resp = requests.post(
        f"{BASE_URL}/smart_collections.json",
        headers=HEADERS,
        json=payload,
    )
    if resp.status_code == 201:
        print(f"  OK    {coll['title']}")
    else:
        print(f"  ERROR {coll['title']} — {resp.status_code}: {resp.text[:300]}")


def main():
    print(f"Creating smart collections on {SHOPIFY_STORE_URL}\n")
    existing = get_existing_handles()
    for coll in COLLECTIONS:
        create_collection(coll, existing)
    print("\nDone.")
    print("\nStill to do manually in Shopify Admin (curated by Louisa):")
    print("  - Staff Picks      (Custom collection — Louisa adds products herself)")
    print("  - NZ Authors       (Custom collection — Louisa adds products herself)")
    print("  - Forthcoming Titles carousel order/curation (Louisa manages manually)")


if __name__ == "__main__":
    main()
