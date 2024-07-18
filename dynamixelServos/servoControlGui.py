import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, QCheckBox
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from PyQt5.QtCore import QThread, pyqtSignal
import threading
from dyn_ax_12p import dynamixel_AX12P
import parameters
from communication import Serial_Port
import cm_530 as cm
import serial
import time

class MotorControlThread(QThread):
    position_updated = pyqtSignal(int, int)

    def __init__(self, port):
        super().__init__()
        self.port = port
        self.motors = {
            2: dynamixel_AX12P(2, self.port),
            6: dynamixel_AX12P(6, self.port),
            8: dynamixel_AX12P(8, self.port)
        }
        self.running = True

    def run(self):
        while self.running:
            for motor_id in self.motors:
                position = cm.present_position(self.port, motor_id)
                self.position_updated.emit(motor_id, position)
            time.sleep(0.01)  # Update every 10ms

    def stop(self):
        self.running = False

    def setPosition(self, motor_id, position):
        cm.goal_position(self.port, motor_id, position)

    def setSpeed(self, motor_id, speed):
        cm.moving_speed(self.port, motor_id, speed)

    def setTorque(self, motor_id, state):
        cm.torque(self.port, motor_id, state)

    def toggleLED(self, motor_id, state):
        cm.led_on_off(self.port, motor_id, 'on' if state else 'off')

class MotorControlGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initMotors()

    def initMotors(self):
        self.port = cm.init_serial('/dev/serial0')
        self.motor_thread = MotorControlThread(self.port)
        self.motor_thread.position_updated.connect(self.updateMotorPosition)
        self.motor_thread.start()

    def updateMotorPosition(self, motor_id, position):
        if motor_id in self.position_labels:
            self.position_labels[motor_id].setText(f'Current Position: {position}')
        if motor_id in [2, 6]:
            self.updateVisualization()

    def setPosition(self, motor_id, position):
        self.motor_thread.setPosition(motor_id, position)

    def setSpeed(self, speed):
        for motor_id in [2, 6, 8]:
            self.motor_thread.setSpeed(motor_id, speed)
        self.speed_label.setText(f'Speed: {speed}')

    def setTorque(self, motor_id, state):
        self.motor_thread.setTorque(motor_id, state)

    def toggleLED(self, motor_id, state):
        self.motor_thread.toggleLED(motor_id, state)

    def closeEvent(self, event):
        self.motor_thread.stop()
        self.motor_thread.wait()
        super().closeEvent(event)
class MotorControlGUI(QMainWindow):
    def __init__(self):
        # ... (previous code)
        self.visualization_timer = QTimer()
        self.visualization_timer.timeout.connect(self.updateVisualization)
        self.visualization_timer.start(50)  # Update every 50ms

    def updateVisualization(self):
        angle1 = self.position_to_angle(self.position_sliders[2].value(), 2)
        angle2 = self.position_to_angle(self.position_sliders[8].value(), 8)
        self.visualization.update_limb(angle1, angle2)


class LimbVisualization(FigureCanvas):
    def __init__(self, parent=None, width=5, height=5, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111, projection='3d')
        super(LimbVisualization, self).__init__(fig)
        self.setParent(parent)
        
        self.axes.set_xlim(-10, 40)
        self.axes.set_ylim(-25, 25)
        self.axes.set_zlim(0, 40)
        self.axes.set_xlabel('X (cm)')
        self.axes.set_ylabel('Y (cm)')
        self.axes.set_zlabel('Z (cm)')
        self.axes.set_title('Limb Visualization')
        
        # Base displacement
        self.base_x = 0
        self.base_y = 0
        self.base_z = 20
        
        self.quiver1 = self.axes.quiver(self.base_x, self.base_y, self.base_z, 0, 0, 14, linewidth=2, arrow_length_ratio=0.1, color='r')
        self.quiver2 = self.axes.quiver(self.base_x, self.base_y, self.base_z + 14, 12.7, 0, 0, linewidth=2, arrow_length_ratio=0.1, color='b')
        
        # Add virtual box
        self.box = self.axes.bar3d(25, -5, 0, 10, 10, 10, shade=True, color='green', alpha=0.8)

    def update_limb(self, angle1, angle2):
        angle1_rad = np.radians(angle1)
        angle2_rad = np.radians(angle2)

        # First limb (length 14 cm)
        x1 = 14 * np.sin(angle1_rad)
        y1 = 0
        z1 = 14 * np.cos(angle1_rad)

        # Second limb (length 12.7 cm), rotated 90 degrees clockwise
        combined_angle = angle1_rad + angle2_rad - np.radians(90)  # Subtract 90 degrees
        x2 = 12.7 * np.sin(combined_angle)
        y2 = 0
        z2 = 12.7 * np.cos(combined_angle)

        self.quiver1.remove()
        self.quiver2.remove()
        self.quiver1 = self.axes.quiver(self.base_x, self.base_y, self.base_z, x1, y1, z1, linewidth=2, arrow_length_ratio=0.1, color='r')
        self.quiver2 = self.axes.quiver(self.base_x + x1, self.base_y + y1, self.base_z + z1, x2, y2, z2, linewidth=2, arrow_length_ratio=0.1, color='b')

        self.axes.set_title(f'Limb Visualization (Angles: {angle1:.1f}°, {angle2:.1f}°)')
        self.draw()

    def move_box(self, x, y, z):
        self.box.remove()
        self.box = self.axes.bar3d(x, y, z, 10, 10, 10, shade=True, color='green', alpha=0.8)
        self.draw()

    def reset_box(self):
        self.box.remove()
        self.box = self.axes.bar3d(25, -5, 0, 10, 10, 10, shade=True, color='green', alpha=0.8)
        self.draw()


class MotorControlGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initMotors()

    def initUI(self):
        self.setWindowTitle('Motor Control GUI')
        self.setGeometry(100, 100, 1000, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        control_layout = QVBoxLayout()
        main_layout.addLayout(control_layout)

        self.position_labels = {}
        self.position_sliders = {}
        self.speed_sliders = {}
        self.torque_checkboxes = {}
        self.led_buttons = {}

        # Combined control for motors 2 and 6
        combined_layout = QVBoxLayout()
        combined_layout.addWidget(QLabel('Combined Control (Motors 2 and 6)'))

        self.combined_slider = QSlider(Qt.Horizontal)
        self.combined_slider.setRange(0, 100)
        self.combined_slider.setValue(50)
        self.combined_slider.valueChanged.connect(self.setCombinedPosition)
        combined_layout.addWidget(QLabel('Limb Position:'))
        combined_layout.addWidget(self.combined_slider)

        self.combined_label = QLabel('Limb Angle: 45.0°')
        combined_layout.addWidget(self.combined_label)

        control_layout.addLayout(combined_layout)

        self.position_labels = {}
        self.position_sliders = {}
        self.torque_checkboxes = {}
        self.led_buttons = {}
        # Add "Fully Extend Arm" button
        self.extend_button = QPushButton('Fully Extend Arm')
        self.extend_button.clicked.connect(self.fullyExtendArm)
        control_layout.addWidget(self.extend_button)
        # Add single speed control for all motors
        speed_layout = QVBoxLayout()
        speed_layout.addWidget(QLabel('Speed (All Motors):'))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(0, 100)
        self.speed_slider.setValue(50)  # Set default to 50%
        self.speed_slider.valueChanged.connect(self.setSpeed)
        speed_layout.addWidget(self.speed_slider)
        self.speed_label = QLabel('Speed: 50%')
        speed_layout.addWidget(self.speed_label)
        control_layout.addLayout(speed_layout)

        # Individual controls for each motor
        for motor_id in [2, 6, 8]:
            motor_layout = QVBoxLayout()
            motor_layout.addWidget(QLabel(f'Motor {motor_id}'))

            position_label = QLabel('Current Goal Position: 512')
            self.position_labels[motor_id] = position_label
            motor_layout.addWidget(position_label)

            pos_slider = QSlider(Qt.Horizontal)
            pos_slider.setRange(200 if motor_id == 8 else 0, 550 if motor_id == 8 else 1024)
            pos_slider.setValue(375 if motor_id == 8 else 512)
            pos_slider.valueChanged.connect(lambda value, id=motor_id: self.setPosition(id, value))
            self.position_sliders[motor_id] = pos_slider
            motor_layout.addWidget(QLabel('Set Position:'))
            motor_layout.addWidget(pos_slider)

            torque_checkbox = QCheckBox('Torque On')
            torque_checkbox.setChecked(True)
            torque_checkbox.stateChanged.connect(lambda state, id=motor_id: self.setTorque(id, state))
            self.torque_checkboxes[motor_id] = torque_checkbox
            motor_layout.addWidget(torque_checkbox)

            led_button = QPushButton('LED')
            led_button.setCheckable(True)
            led_button.clicked.connect(lambda state, id=motor_id: self.toggleLED(id, state))
            self.led_buttons[motor_id] = led_button
            motor_layout.addWidget(led_button)

            control_layout.addLayout(motor_layout)

        # Add "Pick Up Object" button
        self.pickup_button = QPushButton('Pick Up Object')
        self.pickup_button.clicked.connect(self.pickupObject)
        control_layout.addWidget(self.pickup_button)

        # Add "Reset" button
        self.reset_button = QPushButton('Reset')
        self.reset_button.clicked.connect(self.resetAnimation)
        control_layout.addWidget(self.reset_button)

        # Matplotlib visualization
        self.visualization = LimbVisualization(self, width=5, height=5, dpi=100)
        main_layout.addWidget(self.visualization)

        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animatePickup)
        self.animation_step = 0
    def fullyExtendArm(self):
        # Set combined slider (first joint) to 90 degrees
        self.combined_slider.setValue(100)  # 100% of slider range corresponds to 90 degrees
        
        # Set second joint (motor 8) to 90 degrees
        self.position_sliders[8].setValue(200)  # 200 corresponds to 90 degrees for motor 8
        
        # Update the motors
        self.setCombinedPosition(100)
        self.setPosition(8, 200)
        
        # Update visualization
        self.updateVisualization()
    def initMotors(self):
        self.port = cm.init_serial('/dev/serial0')
        self.motors = {
            2: dynamixel_AX12P(2, self.port),
            6: dynamixel_AX12P(6, self.port),
            8: dynamixel_AX12P(8, self.port)
        }
        
        self.motor_limits = {
            2: {'min': 523, 'max': 840},
            6: {'min': 506, 'max': 810},
            8: {'min': 200, 'max': 530}
        }

        # Initialize motor speeds
        for motor_id in self.motors:
            cm.moving_speed(self.port, motor_id, 100)

    def setPosition(self, motor_id, position):
        min_pos = self.motor_limits[motor_id]['min']
        max_pos = self.motor_limits[motor_id]['max']
        clamped_position = max(min_pos, min(position, max_pos))
        cm.goal_position(self.port, motor_id, clamped_position)
        self.position_sliders[motor_id].setValue(clamped_position)
        self.position_labels[motor_id].setText(f'Current Goal Position: {clamped_position}')
        self.updateVisualization()
    
    def setSpeed(self, speed):
        for motor_id in self.motors:
            cm.moving_speed(self.port, motor_id, speed)
        self.speed_label.setText(f'Speed: {speed}')

    def setTorque(self, motor_id, state):
        cm.torque(self.port, motor_id, state == Qt.Checked)

    def toggleLED(self, motor_id, state):
        cm.led_on_off(self.port, motor_id, 'on' if state else 'off')

    def setCombinedPosition(self, value):
        # Calculate positions for motors 2 and 6
        range_2 = self.motor_limits[2]['max'] - self.motor_limits[2]['min']
        range_6 = self.motor_limits[6]['max'] - self.motor_limits[6]['min']
        
        pos_2 = int(self.motor_limits[2]['min'] + (range_2 * value / 100))
        pos_6 = int(self.motor_limits[6]['max'] - (range_6 * value / 100))

        # Set positions
        self.setPosition(2, pos_2)
        self.setPosition(6, pos_6)

        # Update combined label
        angle1 = value * 0.9  # 0-100 to 0-90 degrees
        self.combined_label.setText(f'Limb Angle: {angle1:.1f}°')

        self.updateVisualization()

    def pickupObject(self):
        self.animation_step = 0
        self.animation_timer.start(50)  # Update every 50ms

    def resetAnimation(self):
        self.animation_timer.stop()
        self.animation_step = 0

        # Set combined slider (first joint) to 0 degrees
        self.combined_slider.setValue(0)
        
        # Set second joint (motor 8) to 0 degrees
        # Assuming 0 degrees corresponds to position 550 for motor 8
        self.position_sliders[8].setValue(510)
        self.setCombinedPosition(0)
        self.visualization.reset_box()
        self.updateVisualization()
    def position_to_angle(self, position, motor_id):
        if motor_id == 8:
            # Convert 550-200 to 0-90 degrees
            return ((550 - position) / (550 - 200)) * 90
        elif motor_id in [2, 6]:
            return (position - self.motor_limits[motor_id]['min']) / (self.motor_limits[motor_id]['max'] - self.motor_limits[motor_id]['min']) * 90
        return 0

    def updateVisualization(self):
        angle1 = float(self.combined_label.text().split(': ')[1][:-1])
        angle2 = self.position_to_angle(self.position_sliders[8].value(), 8)
        self.visualization.update_limb(angle1, angle2)

    def animatePickup(self):
        steps = [
            (0, 0),    # Move to initial position
            (90, 90),   # Reach for object
            (0, 0),    # Raise object above robot
        ]
    
        if self.animation_step < len(steps):
            angle1, angle2 = steps[self.animation_step]
            self.combined_slider.setValue(int(angle1 / 0.9))
            self.position_sliders[8].setValue(int(550 - (angle2 / 90) * (550 - 200)))
            
            if self.animation_step == 2:  # Move the box with the gripper
                self.visualization.move_box(0, 0, 34)
            
            self.animation_step += 1
        else:
            self.animation_timer.stop()

    # ... (rest of the code remains the same)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MotorControlGUI()
    ex.show()
    sys.exit(app.exec_())