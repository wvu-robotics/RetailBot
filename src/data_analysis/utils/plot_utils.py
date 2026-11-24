import multiprocessing
import time


class ExternalPlotter:
    def __init__(self):
        self.plot_queue = multiprocessing.Queue()
        self.ready_flag = multiprocessing.Event()  # Synchronization flag
        self.process = multiprocessing.Process(
            target=self._plot_manager, args=(self.plot_queue, self.ready_flag)
        )
        self.process.daemon = True
        self.process.start()

        # Wait for the external process to signal it's ready
        self.ready_flag.wait()  # Block execution until external process is ready

    def _plot_manager(self, plot_queue, ready_flag):
        """Handles external plotting in a separate GUI window."""
        import matplotlib

        matplotlib.use("Qt5Agg")  # Ensure external GUI backend
        import matplotlib.pyplot as plt
        from matplotlib.gridspec import GridSpec
        from PyQt5.QtWidgets import QApplication  # Manually manage the GUI event loop

        app = QApplication([])  # Use empty list instead of sys.argv

        fig = plt.figure(figsize=(8, 6))  # Create external figure
        subplot_map = {}  # Dictionary to track subplot positions
        plots = []  # Store dynamically assigned plots

        ready_flag.set()  # Signal that the process is ready

        while True:
            while not plot_queue.empty():
                data = plot_queue.get()
                if data == "EXIT":
                    plt.close(fig)
                    return

                (plot_data, title, xlabel, ylabel, row, col) = data

                if row is not None and col is not None:
                    subplot_map[(row, col)] = (plot_data, title, xlabel, ylabel)
                else:
                    plots.append((plot_data, title, xlabel, ylabel))

            # Redraw figure only if there are updates
            if subplot_map or plots:
                fig.clear()

                # Determine the grid size dynamically
                n_fixed = len(subplot_map)
                n_dynamic = len(plots)
                n_total = n_fixed + n_dynamic
                ncols = max(2, int(n_total**0.5))  # Keep at least 2 columns
                nrows = (n_total + ncols - 1) // ncols  # Ensure enough rows

                gs = GridSpec(nrows, ncols, figure=fig)

                # Draw fixed subplots
                for (row, col), (
                    plot_data,
                    title,
                    xlabel,
                    ylabel,
                ) in subplot_map.items():
                    ax = fig.add_subplot(gs[row, col])
                    for x, y, label in plot_data:
                        ax.plot(x, y, label=label)
                    ax.set_title(title)
                    ax.set_xlabel(xlabel)
                    ax.set_ylabel(ylabel)
                    ax.legend()

                # Draw dynamically assigned subplots
                for i, (plot_data, title, xlabel, ylabel) in enumerate(plots):
                    row, col = divmod(i + n_fixed, ncols)  # Find next available spot
                    ax = fig.add_subplot(gs[row, col])
                    for x, y, label in plot_data:
                        ax.plot(x, y, label=label)
                    ax.set_title(title)
                    ax.set_xlabel(xlabel)
                    ax.set_ylabel(ylabel)
                    ax.legend()

                                # **Fix overlapping titles**
                fig.tight_layout(rect=[0, 0, 1, 0.92])  # Leave space for suptitle
                fig.subplots_adjust(top=0.85)  # Adjust top margin

                fig.canvas.draw()
                fig.canvas.flush_events()

            app.processEvents()  # Keep the GUI responsive
            time.sleep(0.1)

    def add_plot(self, ax, row=None, col=None):
        """Sends all lines from an Axes object to the external window in a single subplot."""
        lines = ax.get_lines()
        if not lines:
            return  # Skip empty plots

        plot_data = []  # Store all line data together

        for line in lines:
            x, y = line.get_xdata(), line.get_ydata()
            label = line.get_label()
            plot_data.append((x, y, label))

        title = ax.get_title()
        xlabel = ax.get_xlabel()
        ylabel = ax.get_ylabel()

        # Send as one grouped plot
        self.plot_queue.put((plot_data, title, xlabel, ylabel, row, col))