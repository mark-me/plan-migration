        self.df_products = df.rename(
            {
                "Dossiernr.": "id_product",
                "Omschrijving": "name_product",
                "Locatie": "location",
                "Interne/Externe levering": "in_external_delivery",
                "Scrumteam": "scrum_team",
                "PO-er scrumteam": "po",
                "Afnemers": "consumers",
                "Bronnen": "source_systems",
                "Status": "status",
            }
        ).select(
            [
                "id_product",
                "name_product",
                "location",
                "in_external_delivery",
                "scrum_team",
                "po",
                "consumers",
                "source_systems",
                "status",
            ]
        )
