# Spotify

## Goal
This repo serves to house all projects I'll be working on relating to the Spotify API.

#### Project #1
To build my own classifier to predict which songs I'll like from 'Discover Weekly'. Predicted liked songs will be added to a 'vetting' playlist for me to manually review. Whole process will be scheduled to occur on a weekly cadence aligning with 'Discover Weekly' updating every Monday.

## Milestones
As of: 11/11/2023
1. Fetch song data
2. EDA
3. Building classification model
4. Update personal playlist
5. Deploying

As of: 26/03/2024
1. Retrain model with newly labelled data using f1 score since I care more about not mislabelling
2. Set up database
    - BigQuery?
    - CockroachDB? https://www.cockroachlabs.com/blog/serverless-free/
3. Frontload song data to database
    - Manual pipeline via SQLAlchemy?
    - Airbyte?
        - Would need to host it somehow... AWS? EC2?
4. Create flow to update song data after inference
    - Check which songs I didn't move into liked songs and label as dislike
    - Retrain model based on new model
5. Set up DBT project to practice DBT and data modelling

## Blog
https://medium.com/@andychannery/adding-songs-youll-probably-like-automagically-303051539cb6

[Part I](https://medium.com/@andychannery/adding-songs-youll-probably-like-part-i-fetching-song-data-c0b971875eb8)

[Part II](https://medium.com/@andychannery/adding-songs-youll-probably-like-part-ii-eda-37a736f60157)

[Part III](https://medium.com/@andychannery/adding-songs-youll-probably-like-part-iii-building-a-classification-model-dde7b300f3dd)

[Part IV](https://medium.com/@andychannery/adding-songs-youll-probably-like-part-iv-updating-my-personal-playlist-4eef2d02b608)

[Part V](https://medium.com/@andychannery/adding-songs-youll-probably-like-part-v-deploying-29ca3c3d1ec9)
