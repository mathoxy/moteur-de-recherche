# AGENTS.md

## Projet

Moteur de recherche intelligent sur les lois marocaines utilisant une architecture RAG (Retrieval-Augmented Generation).

L'objectif est de permettre aux utilisateurs de rechercher des informations juridiques en langage naturel et d'obtenir des réponses pertinentes accompagnées de références aux textes de loi officiels.

## Stack technique

### Frontend

- Next.js
- TypeScript
- Tailwind CSS

### Backend

- FastAPI
- Python 3.12+

### Stockage

- ChromaDB (base vectorielle)

### IA

- Embeddings multilingues (français/arabe)
- Pipeline RAG
- LLM configurable

## Architecture

Le projet est composé de trois modules principaux :

### 1. Collecte des données

Responsable de la récupération des lois marocaines depuis les sources officielles.

Fonctionnalités :

- Téléchargement de documents PDF ou HTML
- Mise à jour incrémentale

### 2. Ingestion et indexation

Responsable de la préparation des documents pour la recherche sémantique.

Pipeline :

1. Extraction du texte
2. Nettoyage
3. Découpage en chunks
4. Génération des embeddings
5. Indexation dans ChromaDB

### 3. Recherche et génération

Responsable du moteur de recherche juridique.

Pipeline :

1. Réception de la question utilisateur
2. Recherche vectorielle
3. Récupération des passages pertinents
4. Construction du contexte
5. Génération de la réponse
6. Retour des sources utilisées

## Structure cible

backend/

- app/
  - api/
  - services/
  - rag/
  - models/
  - core/

frontend/

- app/
- components/
- services/
- types/

data/

- raw/
- processed/

## Principes importants

- Toutes les réponses doivent être fondées sur les documents indexés.
- Les sources utilisées doivent toujours être retournées à l'utilisateur.
- Ne jamais inventer une référence juridique.
- Conserver les métadonnées des documents (titre, numéro, date, type).
- Favoriser l'indexation par article ou section plutôt que par document complet.
- Séparer clairement la collecte, l'indexation et la recherche.

## Fonctionnalités MVP

- Recherche juridique en langage naturel.
- Consultation des lois indexées.
- Chat juridique basé sur le RAG.
- Affichage des passages sources.
- Interface web simple et responsive.

## Fonctionnalités futures

- Mise à jour automatique des données.
- Support multilingue français/arabe.
- Résumé automatique des lois.
- Historique des recherches.
- Authentification utilisateur.
- Export des résultats.

## Objectif principal

Fournir un accès rapide, fiable et explicable aux lois marocaines grâce à la recherche sémantique et aux modèles d'intelligence artificielle.
