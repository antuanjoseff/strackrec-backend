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
    },
}
# Flamenc: nederlandstalig (Belgïe), mateixos textos que el neerlandès.
TRANSLATIONS["nl-BE"] = TRANSLATIONS["nl"]


def get_texts(lang: str | None) -> Texts:
    if lang in TRANSLATIONS:
        return TRANSLATIONS[lang]  # type: ignore[index]
    return TRANSLATIONS[DEFAULT_LANGUAGE]
