import matplotlib
matplotlib.use('Agg')  # Backend pour environnements sans interface graphique

import os
import json
import streamlit as st
import numpy as np
import seaborn as sns
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd

# Choix de la page sur la sidebar
page = st.sidebar.selectbox("Choisissez une page", ["Ariane Mailanandam", "Dataleon"])

if page == "Ariane Mailanandam":

    st.title("Bienvenue")
    st.markdown("""
    Bonjour! Je m'appelle **Ariane Mailanandam**, je suis actuellement en première année de master en Data Engineering à l'EFREI Paris. 
    """)
    
    st.sidebar.header("About me")
    email = st.sidebar.write("**📧** : ariane.mailanandam@efrei.net")
    location = st.sidebar.write("📍: Ile-de-France")
    phone = st.sidebar.write("📞 : +33 7 81 26 46 28")

    linkedin_url = "https://www.linkedin.com/in/ariane-mailanandam-data-science/"
    st.sidebar.markdown(f"""
        <div style="border: 2px solid #0e76a8; padding: 10px; text-align: center; border-radius: 10px;">
            <a href="{linkedin_url}" target="_blank">
                <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" alt="LinkedIn" style="width:40px; height:40px;">
            </a>
            <p><a href="{linkedin_url}" target="_blank" style="text-decoration:none; color:#0e76a8;">My LinkedIn profile</a></p>
        </div>
    """, unsafe_allow_html=True)

elif page == "Dataleon":

    st.title("Rapport : ")

    # Chemin principal
    main_folder = '/Users/arianemailanandam/Documents/Dataleon'
    subfolders = ['dev', 'test', 'train']

    # Fonction pour charger les fichiers JSON
    def load_json_from_folders(main_folder, subfolders):
        all_json_data = []
        for subfolder in subfolders:
            folder_path = os.path.join(main_folder, subfolder, 'json')
            if os.path.exists(folder_path):
                for filename in os.listdir(folder_path):
                    if filename.endswith('.json'):
                        file_path = os.path.join(folder_path, filename)
                        with open(file_path, 'r') as file:
                            data = json.load(file)
                            if data:  # Vérifie que les données ne sont pas vides
                                all_json_data.append(data)
        return all_json_data

    json_data_all = load_json_from_folders(main_folder, subfolders)

    # Etape 1 : Camembert
    st.header("Combien d'entités Total, Sous-total existe dans le document ?")
    total_count = 0
    subtotal_count = 0

    for data in json_data_all:
        if 'valid_line' in data:
            for line in data['valid_line']:
                if line.get('category') == 'total.total_price':
                    total_count += 1
                elif line.get('category') == 'sub_total.subtotal_price':
                    subtotal_count += 1

    st.write(f"Nombre d'entités Total : {total_count}")
    st.write(f"Nombre d'entités Sous-total : {subtotal_count}")

    if subtotal_count > 0:
        labels = ['Total', 'Sous-total']
        sizes = [total_count, subtotal_count]
    else: 
        labels = ['Total']
        sizes = [total_count]

    if sizes:  # Vérification que les données ne sont pas vides
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)
    else:
        st.write("Aucune donnée valide pour générer le camembert.")

    # Etape 2: Chart image
    def count_taxes_per_image_by_folder(main_folder, subfolder):
        taxes_per_image = {}
        folder_path = os.path.join(main_folder, subfolder, 'json')
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(folder_path, filename)
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                        if 'meta' in data and 'image_id' in data['meta']:
                            image_id = data['meta']['image_id']
                            if 'valid_line' in data:
                                tax_count = sum(1 for line in data['valid_line'] if 'category' in line and 'tax' in line['category'].lower())
                                if tax_count > 1:  # Ne garder que les images avec plus d'une taxe
                                    taxes_per_image[image_id] = tax_count
        return taxes_per_image

    all_tax_data = {}

    for subfolder in subfolders:
        taxes_per_image = count_taxes_per_image_by_folder(main_folder, subfolder)
        all_tax_data[subfolder] = taxes_per_image

    fig, ax = plt.subplots()

    colors = ['blue', 'green', 'red']
    x_offsets = [-0.2, 0, 0.2]

    for idx, (subfolder, taxes_per_image) in enumerate(all_tax_data.items()):
        if taxes_per_image:  # Vérifie qu'il y a des données pour le sous-dossier
            num_images = list(range(1, len(taxes_per_image) + 1))
            tax_counts = list(taxes_per_image.values())
            ax.bar(np.array(num_images) + x_offsets[idx], tax_counts, color=colors[idx], label=subfolder, width=0.2)

    ax.set_xlabel('Nombre d\'images')
    ax.set_ylabel('Nombre total de taxes')
    ax.set_title('Images avec plusieurs taxes dans les sous-dossiers (dev, test, train)')
    ax.legend(title="Sous-dossiers")
    st.pyplot(fig)

    # Etape 3: Position du montant total
    st.header("Le Montant total est souvent situé à quelle position ?")
    def get_total_positions_by_folder(main_folder, subfolder):
        positions = []
        folder_path = os.path.join(main_folder, subfolder, 'json')
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(folder_path, filename)
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                        if 'valid_line' in data:
                            for line in data['valid_line']:
                                if 'category' in line and line['category'] == 'total.total_price':
                                    for word in line['words']:
                                        if 'quad' in word:
                                            x1, y1 = word['quad']['x1'], word['quad']['y1']
                                            x2, y2 = word['quad']['x2'], word['quad']['y2']
                                            positions.append(((x1 + x2) / 2, (y1 + y2) / 2))
        return positions

    all_positions = []
    for subfolder in subfolders:
        positions = get_total_positions_by_folder(main_folder, subfolder)
        all_positions.extend(positions)

    if all_positions:  # Vérifie qu'il y a des positions
        positions_array = np.array(all_positions)
        if positions_array.size > 0:
            heatmap_data, xedges, yedges = np.histogram2d(positions_array[:, 0], positions_array[:, 1], bins=50)
            fig, ax = plt.subplots()
            sns.heatmap(heatmap_data.T, cmap='Blues', ax=ax)
            ax.set_title('Heatmap des positions du Montant Total')
            ax.set_xlabel('Position X')
            ax.set_ylabel('Position Y')
            ax.invert_yaxis()
            st.pyplot(fig)
        else:
            st.write("Aucune position valide trouvée pour créer la heatmap.")
    else:
        st.write("Aucune position pour le Montant Total n'a été trouvée.")

    # Etape 4: Fréquence des entités
    st.header("L'entité la moins représentée ?")
    def count_entities_by_folder(main_folder, subfolder):
        entity_counter = Counter()

        folder_path = os.path.join(main_folder, subfolder, 'json')
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(folder_path, filename)
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                        if 'valid_line' in data:
                            for line in data['valid_line']:
                                if 'category' in line:
                                    entity_counter[line['category']] += 1
        return entity_counter

    total_entity_count = Counter()
    for subfolder in subfolders:
        entity_counter = count_entities_by_folder(main_folder, subfolder)
        total_entity_count.update(entity_counter)

    sorted_entities = total_entity_count.most_common()

    if sorted_entities:  # Vérifie que les entités existent
        entities = [entity for entity, count in sorted_entities]
        frequencies = [count for entity, count in sorted_entities]

        fig, ax = plt.subplots()
        ax.bar(entities, frequencies)
        ax.set_xlabel('Entité')
        ax.set_ylabel('Fréquence')
        ax.set_title('Fréquence des entités')
        plt.xticks(rotation=90)
        st.pyplot(fig)
    else:
        st.write("Aucune entité trouvée pour générer le graphique.")

    # Recommandations pour l'entraînement
    st.header("Quelles sont les recommandations pour entraîner avec ce jeu de données ?")
    st.markdown("""
    ### Étapes recommandées pour l'entraînement :
    - Sélectionner les données pertinentes.
    - Prétraitement et nettoyage des données.
    - Division du jeu de données pour l'entraînement et les tests.
    - Contrôle du surajustement et ajustement du modèle.
    - Améliorations continues avec de nouvelles données.
    """)
