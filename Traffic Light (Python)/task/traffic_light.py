import math
import os
import threading
import time
from dataclasses import dataclass
from enum import Enum

import CircularQueue


class TrafficLight():
    """
    This class represents a traffic light system that controls the opening and closing of roads.
    """
    """ Color codes constants for making terminal output more desirable"""
    ANSI_RED = "\u001B[31m"
    ANSI_GREEN = "\u001B[32m"
    ANSI_YELLOW = "\u001B[33m"
    ANSI_RESET = "\u001B[0m"

    """ Dataclass for representing a road in the traffic light system."""
    @dataclass
    class Road:
        name: str
        opens_at: float  # timestamp road opens

    """ Enum for representing the state of the traffic light system."""

    class TrafficLightControlState(Enum):
        Not_Started = 1
        Menu = 2
        System = 3
        Quit = 0

    """ Enum for representing the commands in the menu."""

    class MenuCommand(Enum):
        ADD = "1"
        DELETE = "2"
        SYSTEM = "3"
        QUIT = "0"

    def __init__(self):
        """Initialize the traffic light."""
        self.welcome()
        self.system_state = self.TrafficLightControlState.Not_Started
        self.num_roads = self.prompt_positive_int("Input the number of roads:")
        self.interval = self.prompt_positive_int("Input the interval:")
        self.queue_thread = threading.Thread(target=self.print_system_settings, args=(self.num_roads, self.interval),
                                             name="QueueThread")
        self.circular_queue = CircularQueue.CircularQueue(self.num_roads)
        self.thread_lock = threading.Lock()

    def prompt_positive_int(self, prompt: str) -> int:
        """Prompt the user for a positive integer.Returns"""
        print(prompt)
        while True:
            try:
                val = int(input())
                if val <= 0:
                    raise ValueError
                return val

            except ValueError:
                print("Incorrect input. Try again:")

    def welcome(self):
        """Print the welcome message."""
        print("Welcome to the traffic management system!")

    def print_controls(self):
        """Print the menu controls."""
        print("Menu:")
        for command in self.MenuCommand:
            print(f"{command.value}: {command.name.title()}")

    def add_road(self) -> None:
        """Add a road and time to open to the traffic light circular queue."""
        with self.thread_lock:
            try:
                road_name_to_add = input("Input road name:")

                if self.circular_queue.is_empty():
                    time_to_open = time.monotonic()
                    road_to_add = self.Road(road_name_to_add, time_to_open)
                else:
                    previous_road = self.circular_queue.peek_back()
                    time_to_open = previous_road.opens_at + self.interval
                    road_to_add = self.Road(road_name_to_add, time_to_open)

                self.circular_queue.enqueue(road_to_add)
                print(f"{road_to_add.name} Added!")

            except OverflowError as exception:
                print(exception)

        self.wait_for_user()

    def delete_road(self) -> None:
        """Delete a road from the traffic light circular queue."""
        with self.thread_lock:
            try:
                deleted_road = self.circular_queue.dequeue()
                print(f"{deleted_road.name} deleted!")

            except IndexError as exception:
                print(exception)

        self.wait_for_user()

    def open_system(self) -> None:
        """Open the traffic light system. Changes the system state machine enables printing system info
           to see the current system state"""
        print("System opened")
        self.system_state = self.TrafficLightControlState.System
        self.wait_for_user()
        self.system_state = self.TrafficLightControlState.Menu

    def parse_command(self, user_input: str) -> MenuCommand | None:
        """Parse the user input and return the corresponding menu command."""
        try:
            return self.MenuCommand(user_input)
        except ValueError:
            return None

    def clear_screen(self) -> None:
        """Clear the screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def wait_for_user(self) -> None:
        """Wait for the user to read the last message."""
        input()

    def shutdown(self, thread) -> None:
        """Shutdown the traffic light system. Sets the system state to Quit and joins the thread."""
        print("Bye!")
        self.system_state = self.TrafficLightControlState.Quit
        thread.join()

    def incorrect_menu_option(self) -> None:
        """Print an error message for an incorrect menu option"""
        print("Incorrect option")
        self.wait_for_user()

    def run_traffic_light(self) -> None:
        """Main function of traffic light. Runs the traffic light system and starts the queue thread."""
        self.queue_thread.start()

        while self.system_state != self.TrafficLightControlState.Quit:
            self.clear_screen()
            self.print_controls()
            user_input = input().strip()
            command = self.parse_command(user_input)

            match command:
                case self.MenuCommand.ADD:
                    self.add_road()
                case self.MenuCommand.DELETE:
                    self.delete_road()
                case self.MenuCommand.SYSTEM:
                    self.open_system()
                case self.MenuCommand.QUIT:
                    self.shutdown(self.queue_thread)
                case _:
                    self.incorrect_menu_option()

    def open_road(self, road: Road, current_timestamp) -> None:
        """Open a road and print the time it will be open."""
        opened_time = math.ceil(road.opens_at + self.interval - current_timestamp)
        if road.opens_at + self.interval - 1 <= current_timestamp:
            print(
                f"{self.ANSI_YELLOW}Road \"{road.name}\" will be open for {opened_time}s.{self.ANSI_RESET}")
        else:
            print(f"{self.ANSI_GREEN}Road \"{road.name}\" will be open for {opened_time}s.{self.ANSI_RESET}")

    def close_road(self, road: Road, current_timestamp) -> None:
        """Close a road and print the time it will be closed."""
        closed_time = math.ceil(road.opens_at - current_timestamp)
        print(f"{self.ANSI_RED}Road \"{road.name}\" will be closed for {closed_time}s.{self.ANSI_RESET}")

    def print_system_settings(self, num_roads: int, interval: int) -> None:
        """Print the system settings, roads with their respective open/closed times and
           elapsed time from the start of the traffic light system."""
        start_timestamp = time.monotonic()
        next_print_time = start_timestamp + 1

        while self.system_state != self.TrafficLightControlState.Quit:
            current_timestamp = time.monotonic()
            elapsed_time = math.ceil(current_timestamp - start_timestamp)

            if self.system_state == self.TrafficLightControlState.System and current_timestamp >= next_print_time:
                self.clear_screen()
                print(f"! {elapsed_time}s. have passed since system startup !")
                print(f"! Number of roads: {num_roads} !")
                print(f"! Interval: {interval} !")
                print("")

                for road_count in range(self.circular_queue.size):
                    self.thread_lock.acquire()
                    road = self.circular_queue.dequeue()

                    if road.opens_at + interval < current_timestamp:
                        if self.circular_queue.size == 0:
                            road.opens_at += interval
                        else:
                            last_road = self.circular_queue.peek_back()
                            road.opens_at = last_road.opens_at + interval

                    if (road.opens_at <= current_timestamp) and (road.opens_at + interval >= current_timestamp):
                        self.open_road(road, current_timestamp)
                    else:
                        self.close_road(road, current_timestamp)

                    self.circular_queue.enqueue(road)
                    self.thread_lock.release()

                print("")
                print("! Press \"Enter\" to open menu !")

                next_print_time = current_timestamp + 1
            # time.sleep(0.02)


if __name__ == "__main__":
    traffic_light = TrafficLight()
    traffic_light.run_traffic_light()
