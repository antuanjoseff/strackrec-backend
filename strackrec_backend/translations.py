"""Textos multilingües per als correus i pàgines de confirmació de mapes."""

from typing import Literal, TypedDict

Lang = Literal["ca", "es", "fr", "it", "de", "nl", "nl-BE", "lb", "en"]

SUPPORTED_LANGUAGES: tuple[Lang, ...] = (
    "ca",
    "es",
    "fr",
    "it",
    "de",
    "nl",
    "nl-BE",
    "lb",
    "en",
)
DEFAULT_LANGUAGE: Lang = "ca"


class Texts(TypedDict):
    request_success_message: str
    confirm_subject: str
    confirm_body: str
    page_title: str
    page_heading: str
    page_text: str
    page_button: str
    err_expired: str
    err_invalid: str
    err_already_confirmed: str
    err_queue: str
    err_email_confirmation: str
    queued_subject: str
    queued_body: str
    queued_success_message: str
    invalid_map_name: str
    invalid_map_url: str
    generated_map_description: str
    map_generation_failed_subject: str
    map_generation_failed_body: str
    map_generation_ready_subject: str
    map_generation_ready_body: str


TRANSLATIONS: dict[Lang, Texts] = {
    "ca": {
        "request_success_message": "Hem enviat un enllaç de confirmació al correu indicat.",
        "confirm_subject": "Confirma la sol·licitud del mapa",
        "confirm_body": (
            "Per confirmar la generació del mapa, obre aquest enllaç:\n\n"
            "{confirmation_url}\n\n"
            "L'enllaç caduca al cap de 24 hores i només es pot utilitzar una vegada."
        ),
        "page_title": "Confirma la sol·licitud del mapa",
        "page_heading": "Confirma la sol·licitud del mapa",
        "page_text": "Prem el botó per afegir la generació del mapa a la cua.",
        "page_button": "Confirma la sol·licitud",
        "err_expired": "L'enllaç de confirmació ha caducat",
        "err_invalid": "L'enllaç de confirmació no és vàlid",
        "err_already_confirmed": "Aquesta sol·licitud ja s'ha confirmat",
        "err_queue": "No s'ha pogut afegir la sol·licitud a la cua",
        "err_email_confirmation": "No s'ha pogut enviar el correu de confirmació",
        "queued_subject": "La sol·licitud del mapa és a la cua",
        "queued_body": (
            "La sol·licitud '{name}' s'ha afegit a la cua.\n"
            "Posició estimada: {queue_position}.\n"
            "Identificador de la tasca: {job_id}."
        ),
        "queued_success_message": "La sol·licitud s'ha afegit a la cua.",
        "invalid_map_name": "El nom ha de contenir entre 1 i 80 caràcters vàlids",
        "invalid_map_url": "La URL ha de ser un fitxer .osm.pbf de download.geofabrik.de",
        "generated_map_description": "Mapa offline de la regió {name}",
        "map_generation_failed_subject": "No s'ha pogut generar el mapa",
        "map_generation_failed_body": "La generació de '{name}' ha fallat. Identificador de la tasca: {task_id}.",
        "map_generation_ready_subject": "El mapa ja està disponible",
        "map_generation_ready_body": (
            "La generació de '{name}' ha acabat correctament.\n\n"
            "Descarrega el mapa (disponible durant 24 hores):\n{download_url}\n\n"
            "Identificador de la tasca: {task_id}."
        ),
    },
    "es": {
        "request_success_message": "Hemos enviado un enlace de confirmación al correo indicado.",
        "confirm_subject": "Confirma la solicitud del mapa",
        "confirm_body": (
            "Para confirmar la generación del mapa, abre este enlace:\n\n"
            "{confirmation_url}\n\n"
            "El enlace caduca a las 24 horas y solo se puede usar una vez."
        ),
        "page_title": "Confirma la solicitud del mapa",
        "page_heading": "Confirma la solicitud del mapa",
        "page_text": "Pulsa el botón para añadir la generación del mapa a la cola.",
        "page_button": "Confirmar la solicitud",
        "err_expired": "El enlace de confirmación ha caducado",
        "err_invalid": "El enlace de confirmación no es válido",
        "err_already_confirmed": "Esta solicitud ya se ha confirmado",
        "err_queue": "No se ha podido añadir la solicitud a la cola",
        "err_email_confirmation": "No se ha podido enviar el correo de confirmación",
        "queued_subject": "La solicitud del mapa está en cola",
        "queued_body": (
            "La solicitud '{name}' se ha añadido a la cola.\n"
            "Posición estimada: {queue_position}.\n"
            "Identificador de la tarea: {job_id}."
        ),
        "queued_success_message": "La solicitud se ha añadido a la cola.",
        "invalid_map_name": "El nombre debe contener entre 1 y 80 caracteres válidos",
        "invalid_map_url": "La URL debe ser un archivo .osm.pbf de download.geofabrik.de",
        "generated_map_description": "Mapa sin conexión de la región {name}",
        "map_generation_failed_subject": "No se ha podido generar el mapa",
        "map_generation_failed_body": "Ha fallado la generación de '{name}'. Identificador de la tarea: {task_id}.",
        "map_generation_ready_subject": "El mapa ya está disponible",
        "map_generation_ready_body": (
            "La generación de '{name}' ha terminado correctamente.\n\n"
            "Descarga el mapa (disponible durante 24 horas):\n{download_url}\n\n"
            "Identificador de la tarea: {task_id}."
        ),
    },
    "fr": {
        "request_success_message": "Nous avons envoyé un lien de confirmation à l'adresse indiquée.",
        "confirm_subject": "Confirmez la demande de carte",
        "confirm_body": (
            "Pour confirmer la génération de la carte, ouvrez ce lien :\n\n"
            "{confirmation_url}\n\n"
            "Le lien expire au bout de 24 heures et ne peut être utilisé qu'une seule fois."
        ),
        "page_title": "Confirmez la demande de carte",
        "page_heading": "Confirmez la demande de carte",
        "page_text": "Appuyez sur le bouton pour ajouter la génération de la carte à la file d'attente.",
        "page_button": "Confirmer la demande",
        "err_expired": "Le lien de confirmation a expiré",
        "err_invalid": "Le lien de confirmation n'est pas valide",
        "err_already_confirmed": "Cette demande a déjà été confirmée",
        "err_queue": "Impossible d'ajouter la demande à la file d'attente",
        "err_email_confirmation": "Impossible d'envoyer l'e-mail de confirmation",
        "queued_subject": "La demande de carte est dans la file d'attente",
        "queued_body": (
            "La demande '{name}' a été ajoutée à la file d'attente.\n"
            "Position estimée : {queue_position}.\n"
            "Identifiant de la tâche : {job_id}."
        ),
        "queued_success_message": "La demande a été ajoutée à la file d'attente.",
        "invalid_map_name": "Le nom doit contenir entre 1 et 80 caractères valides",
        "invalid_map_url": "L'URL doit être un fichier .osm.pbf de download.geofabrik.de",
        "generated_map_description": "Carte hors ligne de la région {name}",
        "map_generation_failed_subject": "La génération de la carte a échoué",
        "map_generation_failed_body": "La génération de '{name}' a échoué. Identifiant de la tâche : {task_id}.",
        "map_generation_ready_subject": "La carte est disponible",
        "map_generation_ready_body": (
            "La génération de '{name}' s'est terminée correctement.\n\n"
            "Téléchargez la carte (disponible pendant 24 heures) :\n{download_url}\n\n"
            "Identifiant de la tâche : {task_id}."
        ),
    },
    "it": {
        "request_success_message": "Abbiamo inviato un link di conferma all'indirizzo indicato.",
        "confirm_subject": "Conferma la richiesta della mappa",
        "confirm_body": (
            "Per confermare la generazione della mappa, apri questo link:\n\n"
            "{confirmation_url}\n\n"
            "Il link scade dopo 24 ore e può essere usato una sola volta."
        ),
        "page_title": "Conferma la richiesta della mappa",
        "page_heading": "Conferma la richiesta della mappa",
        "page_text": "Premi il pulsante per aggiungere la generazione della mappa alla coda.",
        "page_button": "Conferma la richiesta",
        "err_expired": "Il link di conferma è scaduto",
        "err_invalid": "Il link di conferma non è valido",
        "err_already_confirmed": "Questa richiesta è già stata confermata",
        "err_queue": "Non è stato possibile aggiungere la richiesta alla coda",
        "err_email_confirmation": "Non è stato possibile inviare l'e-mail di conferma",
        "queued_subject": "La richiesta della mappa è in coda",
        "queued_body": (
            "La richiesta '{name}' è stata aggiunta alla coda.\n"
            "Posizione stimata: {queue_position}.\n"
            "Identificativo del task: {job_id}."
        ),
        "queued_success_message": "La richiesta è stata aggiunta alla coda.",
        "invalid_map_name": "Il nome deve contenere da 1 a 80 caratteri validi",
        "invalid_map_url": "L'URL deve essere un file .osm.pbf di download.geofabrik.de",
        "generated_map_description": "Mappa offline della regione {name}",
        "map_generation_failed_subject": "Impossibile generare la mappa",
        "map_generation_failed_body": "La generazione di '{name}' non è riuscita. Identificativo del task: {task_id}.",
        "map_generation_ready_subject": "La mappa è disponibile",
        "map_generation_ready_body": (
            "La generazione di '{name}' è terminata correttamente.\n\n"
            "Scarica la mappa (disponibile per 24 ore):\n{download_url}\n\n"
            "Identificativo del task: {task_id}."
        ),
    },
    "de": {
        "request_success_message": "Wir haben einen Bestätigungslink an die angegebene E-Mail-Adresse gesendet.",
        "confirm_subject": "Bestätige die Kartenanfrage",
        "confirm_body": (
            "Um die Erstellung der Karte zu bestätigen, öffne diesen Link:\n\n"
            "{confirmation_url}\n\n"
            "Der Link läuft nach 24 Stunden ab und kann nur einmal verwendet werden."
        ),
        "page_title": "Bestätige die Kartenanfrage",
        "page_heading": "Bestätige die Kartenanfrage",
        "page_text": "Drücke die Schaltfläche, um die Kartenerstellung zur Warteschlange hinzuzufügen.",
        "page_button": "Anfrage bestätigen",
        "err_expired": "Der Bestätigungslink ist abgelaufen",
        "err_invalid": "Der Bestätigungslink ist ungültig",
        "err_already_confirmed": "Diese Anfrage wurde bereits bestätigt",
        "err_queue": "Die Anfrage konnte nicht zur Warteschlange hinzugefügt werden",
        "err_email_confirmation": "Die Bestätigungs-E-Mail konnte nicht gesendet werden",
        "queued_subject": "Die Kartenanfrage befindet sich in der Warteschlange",
        "queued_body": (
            "Die Anfrage '{name}' wurde zur Warteschlange hinzugefügt.\n"
            "Geschätzte Position: {queue_position}.\n"
            "Aufgaben-ID: {job_id}."
        ),
        "queued_success_message": "Die Anfrage wurde zur Warteschlange hinzugefügt.",
        "invalid_map_name": "Der Name muss zwischen 1 und 80 gültige Zeichen enthalten",
        "invalid_map_url": "Die URL muss eine .osm.pbf-Datei von download.geofabrik.de sein",
        "generated_map_description": "Offline-Karte der Region {name}",
        "map_generation_failed_subject": "Die Karte konnte nicht erstellt werden",
        "map_generation_failed_body": "Die Erstellung von '{name}' ist fehlgeschlagen. Aufgaben-ID: {task_id}.",
        "map_generation_ready_subject": "Die Karte ist verfügbar",
        "map_generation_ready_body": (
            "Die Erstellung von '{name}' wurde erfolgreich abgeschlossen.\n\n"
            "Lade die Karte herunter (24 Stunden verfügbar):\n{download_url}\n\n"
            "Aufgaben-ID: {task_id}."
        ),
    },
    "nl": {
        "request_success_message": "We hebben een bevestigingslink naar het opgegeven e-mailadres gestuurd.",
        "confirm_subject": "Bevestig de kaartaanvraag",
        "confirm_body": (
            "Open deze link om het genereren van de kaart te bevestigen:\n\n"
            "{confirmation_url}\n\n"
            "De link verloopt na 24 uur en kan maar één keer worden gebruikt."
        ),
        "page_title": "Bevestig de kaartaanvraag",
        "page_heading": "Bevestig de kaartaanvraag",
        "page_text": "Druk op de knop om het genereren van de kaart aan de wachtrij toe te voegen.",
        "page_button": "Aanvraag bevestigen",
        "err_expired": "De bevestigingslink is verlopen",
        "err_invalid": "De bevestigingslink is ongeldig",
        "err_already_confirmed": "Deze aanvraag is al bevestigd",
        "err_queue": "De aanvraag kon niet aan de wachtrij worden toegevoegd",
        "err_email_confirmation": "De bevestigingsmail kon niet worden verzonden",
        "queued_subject": "De kaartaanvraag staat in de wachtrij",
        "queued_body": (
            "De aanvraag '{name}' is toegevoegd aan de wachtrij.\n"
            "Geschatte positie: {queue_position}.\n"
            "Taak-ID: {job_id}."
        ),
        "queued_success_message": "De aanvraag is aan de wachtrij toegevoegd.",
        "invalid_map_name": "De naam moet 1 tot 80 geldige tekens bevatten",
        "invalid_map_url": "De URL moet een .osm.pbf-bestand van download.geofabrik.de zijn",
        "generated_map_description": "Offlinekaart van de regio {name}",
        "map_generation_failed_subject": "De kaart kon niet worden gegenereerd",
        "map_generation_failed_body": "Het genereren van '{name}' is mislukt. Taak-ID: {task_id}.",
        "map_generation_ready_subject": "De kaart is beschikbaar",
        "map_generation_ready_body": (
            "Het genereren van '{name}' is voltooid.\n\n"
            "Download de kaart (24 uur beschikbaar):\n{download_url}\n\n"
            "Taak-ID: {task_id}."
        ),
    },
    "lb": {
        "request_success_message": "Mir hunn e Bestätegungslink un déi uginn E-Mail geschéckt.",
        "confirm_subject": "Bestätegt d'Ufro fir d'Kaart",
        "confirm_body": (
            "Fir d'Erstelle vun der Kaart ze bestätegen, mach dëse Link op:\n\n"
            "{confirmation_url}\n\n"
            "De Link leeft no 24 Stonnen of a kann nëmmen eemol benotzt ginn."
        ),
        "page_title": "Bestätegt d'Ufro fir d'Kaart",
        "page_heading": "Bestätegt d'Ufro fir d'Kaart",
        "page_text": "Dréckt op de Knäppchen fir d'Erstelle vun der Kaart an d'Warteschlaang ze setzen.",
        "page_button": "Ufro bestätegen",
        "err_expired": "De Bestätegungslink ass ofgelaf",
        "err_invalid": "De Bestätegungslink ass net gülteg",
        "err_already_confirmed": "Dës Ufro gouf schonn bestätegt",
        "err_queue": "D'Ufro konnt net an d'Warteschlaang gesat ginn",
        "err_email_confirmation": "D'Bestätegungs-E-Mail konnt net geschéckt ginn",
        "queued_subject": "D'Ufro fir d'Kaart ass an der Warteschlaang",
        "queued_body": (
            "D'Ufro '{name}' gouf an d'Warteschlaang gesat.\n"
            "Geschätzte Positioun: {queue_position}.\n"
            "Task-ID: {job_id}."
        ),
        "queued_success_message": "D'Ufro gouf an d'Warteschlaang gesat.",
        "invalid_map_name": "Den Numm muss tëscht 1 an 80 gülteg Zeechen enthalen",
        "invalid_map_url": "D'URL muss eng .osm.pbf-Datei vun download.geofabrik.de sinn",
        "generated_map_description": "Offline-Kaart vun der Regioun {name}",
        "map_generation_failed_subject": "D'Kaart konnt net erstallt ginn",
        "map_generation_failed_body": "D'Erstelle vun '{name}' ass feelgeschloen. Task-ID: {task_id}.",
        "map_generation_ready_subject": "D'Kaart ass disponibel",
        "map_generation_ready_body": (
            "D'Erstelle vun '{name}' ass erfollegräich ofgeschloss.\n\n"
            "Luet d'Kaart erof (24 Stonne disponibel):\n{download_url}\n\n"
            "Task-ID: {task_id}."
        ),
    },
    "en": {
        "request_success_message": "We've sent a confirmation link to the given email.",
        "confirm_subject": "Confirm the map request",
        "confirm_body": (
            "To confirm the map generation, open this link:\n\n"
            "{confirmation_url}\n\n"
            "The link expires after 24 hours and can only be used once."
        ),
        "page_title": "Confirm the map request",
        "page_heading": "Confirm the map request",
        "page_text": "Press the button to add the map generation to the queue.",
        "page_button": "Confirm the request",
        "err_expired": "The confirmation link has expired",
        "err_invalid": "The confirmation link is not valid",
        "err_already_confirmed": "This request has already been confirmed",
        "err_queue": "The request could not be added to the queue",
        "err_email_confirmation": "The confirmation email could not be sent",
        "queued_subject": "The map request is in the queue",
        "queued_body": (
            "The request '{name}' has been added to the queue.\n"
            "Estimated position: {queue_position}.\n"
            "Task ID: {job_id}."
        ),
        "queued_success_message": "The request has been added to the queue.",
        "invalid_map_name": "The name must contain between 1 and 80 valid characters",
        "invalid_map_url": "The URL must be a .osm.pbf file from download.geofabrik.de",
        "generated_map_description": "Offline map of the {name} region",
        "map_generation_failed_subject": "The map could not be generated",
        "map_generation_failed_body": "Generation of '{name}' failed. Task ID: {task_id}.",
        "map_generation_ready_subject": "The map is ready",
        "map_generation_ready_body": (
            "Generation of '{name}' completed successfully.\n\n"
            "Download the map (available for 24 hours):\n{download_url}\n\n"
            "Task ID: {task_id}."
        ),
    },
}
# Flamenc: nederlandstalig (Belgïe), mateixos textos que el neerlandès.
TRANSLATIONS["nl-BE"] = TRANSLATIONS["nl"]


def get_texts(lang: str | None) -> Texts:
    if lang in TRANSLATIONS:
        return TRANSLATIONS[lang]  # type: ignore[index]
    return TRANSLATIONS[DEFAULT_LANGUAGE]
