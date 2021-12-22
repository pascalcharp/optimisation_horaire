from ortools.sat.python import cp_model

# Premier exercice de génération automatique d'horaire pour le département
# Essentiellement une transcription de l'exemple sur le site d'OR Tools
# https://developers.google.com/optimization/scheduling/employee_scheduling
# Il s'agit donc ici d'un exercice préliminaire de faisabilité

# Le résolveur est l'objet model
# On ajoute à celui-ci un modèle de données
# Et des contraintes


# Modèle de données:
#
# Un dictionnaire de bool. Pour l'instant ce modèle semble gaspiller de la mémoire puisque la majorité des entrées vaut
# false.  C'est à repenser...
#
# Matrice ordre: cette structure de données contiendra la solution cherchée
#
# Chaque anesthésiste a un numéro, chaque jour a un numéro et chaque choix de salle est aussi numéroté.
# Chaque entrée du dictionnaire est repérée par le tuple (anesthésiste, jour, choix)
# Si l'anesthésiste numéro 3 a le huitième choix au jour 42 alors ordre[(3, 42, 8)] == true
#

def main():
    n_anesthesistes = 15
    n_choix = 10
    n_jours = 21

    tousAnesthesistes = range(n_anesthesistes)
    tousChoix = range(n_choix)
    tousJours = range(n_jours)

    model = cp_model.CpModel()

    ordre = {}
    for anesthesiste in tousAnesthesistes:
        for jour in tousJours:
            for choix in tousChoix:
                ordre[(anesthesiste, jour, choix)] = model.NewBoolVar('choix_%id%ij%io' % (anesthesiste, jour, choix))

    # CONTRAINTES

    # Contraintes fondamentales:
    # Unicité du choix: chaque anesthésiste a un choix maximum par jour

    for jour in tousJours:
        for anesthesiste in tousAnesthesistes:
            model.Add((sum(ordre[(anesthesiste, jour, choix)] for choix in tousChoix) <= 1))

    # Contraintes fondamentales:
    # Pour chaque journée, chaque salle disponible doit être occupée par un, et un seul anesthésiste

    for jour in tousJours:
        for choix in tousChoix:
            model.Add((sum(ordre[(anesthesiste, jour, choix)] for anesthesiste in tousAnesthesistes) == 1))

    # Contraintes fondamentales:
    # Les choix,  doivent être répartis également sur tous les anesthésistes

    nombre_minimal_garde = n_jours // n_anesthesistes
    premiersChoix = range(n_choix)

    for anesthesiste in tousAnesthesistes:
        for choix in premiersChoix:
            model.Add((sum(ordre[(anesthesiste, jour, choix)] for jour in tousJours) >= nombre_minimal_garde))

    nombre_maximal_garde = nombre_minimal_garde
    if n_jours % n_anesthesistes != 0:
        nombre_maximal_garde = nombre_maximal_garde + 1

    for anesthesiste in tousAnesthesistes:
        for choix in premiersChoix:
            model.Add((sum(ordre[(anesthesiste, jour, choix)] for jour in tousJours) <= nombre_maximal_garde))

    # Configuration du résolveur de modèle
    # Aucune optimisation n'est demandée ici, on cherche seulement des solutions faisables

    resolveur = cp_model.CpSolver()
    resolveur.parameters.linearization_level = 0
    resolveur.parameters.enumerate_all_solutions = True

# Classe permettant d'afficher les solutions obtenues

    class AfficherDesHorairesTrouves(cp_model.CpSolverSolutionCallback):

        def __init__(self, p_ordre, n_anesth, pn_jours, pn_choix, maximum):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self._ordre = p_ordre
            self._n_anesthesistes = n_anesth
            self._n_jours = pn_jours
            self._n_choix = pn_choix
            self._maximum = maximum
            self._n_solutions = 0

        def on_solution_callback(self):
            self._n_solutions += 1
            print ('Solution %i'% self._n_solutions)
            print ('JOUR: ', end='')
            for jour in range(self._n_jours):
                print('%6d' % jour, end='')
            print('\n')
            for anesthesiste in range(self._n_anesthesistes):
                print('AN%2d: ' % anesthesiste, end='')

                for jour in range(self._n_jours):
                    assignation = False
                    for choix in range(self._n_choix):
                        if self.Value(self._ordre[(anesthesiste, jour, choix)]):
                            assignation = True
                            print('%6d' % choix, end='')
                    if not assignation:
                        print('     X', end='')
                print('\n')

            if (self._n_solutions >= self._maximum):
                print('Nombre maximal de solutions atteint')
                self.StopSearch()

        def solution_count(self):
            return self._n_solutions

    afficheur = AfficherDesHorairesTrouves(ordre, n_anesthesistes, n_jours, n_choix, 5)
    resolveur.Solve(model, afficheur)

# Programme principal

if __name__ == '__main__':
    main()

# Création de l'objet afficheur




