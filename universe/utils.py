import csv
import statistics


def save_statistics_to_csv(ants, filename, round_counter):
    """Save statistics about the ants to a CSV file."""

    # Calculating statistics
    total_ants = len(ants)
    alive_ants = sum(1 for ant in ants if ant.alive)
    dead_ants = total_ants - alive_ants

    black_ants_alive = sum(
        1 for ant in ants if type(ant).__name__ == "BlackAnt" and ant.alive
    )
    red_ants_alive = alive_ants - black_ants_alive
    worker_ants_alive = sum(
        1 for ant in ants if ant.role.name == "WORKER" and ant.alive
    )
    soldier_ants_alive = sum(
        1 for ant in ants if ant.role.name == "SOLDIER" and ant.alive
    )
    queen_ants_alive = sum(1 for ant in ants if ant.role.name == "QUEEN" and ant.alive)

    black_ants_dead = sum(
        1 for ant in ants if type(ant).__name__ == "BlackAnt" and not ant.alive
    )
    red_ants_dead = dead_ants - black_ants_dead
    worker_ants_dead = sum(
        1 for ant in ants if ant.role.name == "WORKER" and not ant.alive
    )
    soldier_ants_dead = sum(
        1 for ant in ants if ant.role.name == "SOLDIER" and not ant.alive
    )
    queen_ants_dead = sum(
        1 for ant in ants if ant.role.name == "QUEEN" and not ant.alive
    )

    # Calculating the average health, speed, and damage for alive ants
    if alive_ants > 0:
        avg_health = statistics.mean(ant.health for ant in ants if ant.alive)
        avg_speed = statistics.mean(ant.speed for ant in ants if ant.alive)
        avg_damage = statistics.mean(ant.damage for ant in ants if ant.alive)
    else:
        avg_health = None
        avg_speed = None
        avg_damage = None

    # Opening the file in append mode
    with open(filename, "a+", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # Moving the reader to the beginning of the file
        csvfile.seek(0)
        # Writing the header row if the file is empty or the first row is not the headers
        first_line = csvfile.readline().strip().split(",")
        headers = [
            "ROUND",
            "total_ants",
            "alive_ants",
            "dead_ants",
            "black_ants_alive",
            "red_ants_alive",
            "worker_ants_alive",
            "soldier_ants_alive",
            "queen_ants_alive",
            "black_ants_dead",
            "red_ants_dead",
            "worker_ants_dead",
            "soldier_ants_dead",
            "queen_ants_dead",
            "avg_health",
            "avg_speed",
            "avg_damage",
        ]
        if not first_line or first_line != headers:
            writer.writerow(headers)

        # Writing the statistics to the file
        writer.writerow(
            [
                round_counter,
                total_ants,
                alive_ants,
                dead_ants,
                black_ants_alive,
                red_ants_alive,
                worker_ants_alive,
                soldier_ants_alive,
                queen_ants_alive,
                black_ants_dead,
                red_ants_dead,
                worker_ants_dead,
                soldier_ants_dead,
                queen_ants_dead,
                avg_health,
                avg_speed,
                avg_damage,
            ]
        )
