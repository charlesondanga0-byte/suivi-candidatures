const STATUTS = ["À envoyer", "Envoyée", "Entretien", "Offre", "Refus"];
const CLASSES = {
  "À envoyer": "a-envoyer",
  "Envoyée": "envoyee",
  "Entretien": "entretien",
  "Offre": "offre",
  "Refus": "refus",
};

let candidatures = [];

async function api(url, options = {}) {
  const reponse = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!reponse.ok) {
    const erreur = await reponse.json().catch(() => ({}));
    const detail = typeof erreur.detail === "string" ? erreur.detail : "Erreur " + reponse.status;
    throw new Error(detail);
  }
  return reponse.status === 204 ? null : reponse.json();
}

function el(balise, proprietes = {}, ...enfants) {
  const element = document.createElement(balise);
  Object.assign(element, proprietes);
  element.append(...enfants);
  return element;
}

function formaterDate(texte) {
  return new Date(texte + "T00:00:00").toLocaleDateString("fr-FR");
}

function carte(titre, valeur, classe) {
  return el(
    "div",
    { className: "carte " + classe },
    el("strong", { textContent: valeur }),
    el("span", { textContent: titre })
  );
}

async function chargerStats() {
  const s = await api("/api/stats");
  const conteneur = document.getElementById("stats");
  conteneur.replaceChildren(carte("Total", s.total, ""));
  for (const statut of STATUTS) {
    conteneur.append(carte(statut, s.par_statut[statut] || 0, CLASSES[statut]));
  }
}

async function chargerListe() {
  const statut = document.getElementById("filtre-statut").value;
  const url = "/api/candidatures" + (statut ? "?statut=" + encodeURIComponent(statut) : "");
  candidatures = await api(url);
  afficher();
}

function afficher() {
  const terme = document.getElementById("recherche").value.trim().toLowerCase();
  const lignes = candidatures.filter((c) =>
    (c.entreprise + " " + c.poste).toLowerCase().includes(terme)
  );
  const corps = document.getElementById("corps");
  corps.replaceChildren(...lignes.map(ligne));
  document.getElementById("vide").hidden = lignes.length > 0;
}

function ligne(c) {
  const lienValide = c.lien && /^https?:\/\//i.test(c.lien);
  const entreprise = lienValide
    ? el("a", {
        href: c.lien,
        target: "_blank",
        rel: "noopener noreferrer",
        textContent: c.entreprise,
      })
    : document.createTextNode(c.entreprise);

  return el(
    "tr",
    {},
    el("td", {}, entreprise),
    el("td", { textContent: c.poste }),
    el("td", {}, el("span", { className: "badge " + CLASSES[c.statut], textContent: c.statut })),
    el("td", { textContent: formaterDate(c.date_candidature) }),
    el(
      "td",
      { className: "actions" },
      el("button", { className: "icone", title: "Modifier", textContent: "✎", onclick: () => ouvrirFormulaire(c) }),
      el("button", { className: "icone", title: "Supprimer", textContent: "🗑", onclick: () => supprimer(c) })
    )
  );
}

const dialogue = document.getElementById("dialogue");
const formulaire = document.getElementById("formulaire");

function ouvrirFormulaire(c = null) {
  formulaire.reset();
  const f = formulaire.elements;
  document.getElementById("titre-dialogue").textContent = c
    ? "Modifier la candidature"
    : "Nouvelle candidature";
  f.id.value = c ? c.id : "";
  f.entreprise.value = c ? c.entreprise : "";
  f.poste.value = c ? c.poste : "";
  f.lien.value = c && c.lien ? c.lien : "";
  f.statut.value = c ? c.statut : STATUTS[0];
  f.date_candidature.value = c
    ? c.date_candidature
    : new Date().toLocaleDateString("sv-SE");
  f.notes.value = c && c.notes ? c.notes : "";
  dialogue.showModal();
}

async function supprimer(c) {
  if (!confirm("Supprimer la candidature « " + c.entreprise + " » ?")) return;
  try {
    await api("/api/candidatures/" + c.id, { method: "DELETE" });
    await rafraichir();
  } catch (erreur) {
    alert(erreur.message);
  }
}

async function rafraichir() {
  await Promise.all([chargerStats(), chargerListe()]);
}

formulaire.addEventListener("submit", async (evenement) => {
  evenement.preventDefault();
  const f = formulaire.elements;
  const donnees = {
    entreprise: f.entreprise.value.trim(),
    poste: f.poste.value.trim(),
    lien: f.lien.value.trim() || null,
    statut: f.statut.value,
    date_candidature: f.date_candidature.value,
    notes: f.notes.value.trim() || null,
  };
  const id = f.id.value;
  try {
    await api(id ? "/api/candidatures/" + id : "/api/candidatures", {
      method: id ? "PUT" : "POST",
      body: JSON.stringify(donnees),
    });
    dialogue.close();
    await rafraichir();
  } catch (erreur) {
    alert(erreur.message);
  }
});

document.getElementById("nouvelle").addEventListener("click", () => ouvrirFormulaire());
document.getElementById("annuler").addEventListener("click", () => dialogue.close());
document.getElementById("filtre-statut").addEventListener("change", chargerListe);
document.getElementById("recherche").addEventListener("input", afficher);

for (const statut of STATUTS) {
  document.getElementById("filtre-statut").append(el("option", { value: statut, textContent: statut }));
  formulaire.elements.statut.append(el("option", { value: statut, textContent: statut }));
}

rafraichir().catch((erreur) => alert(erreur.message));
