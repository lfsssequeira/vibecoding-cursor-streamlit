#!/usr/bin/env python3
import ctypes
import time
import signal
import sys

# CoreGraphics constants
kCGEventMouseMoved = 5
kCGHIDEventTap = 0
kCGMouseButtonLeft = 0


class CoreGraphics:
	def __init__(self):
		self.cg = ctypes.CDLL(
			"/System/Library/Frameworks/ApplicationServices.framework/Frameworks/CoreGraphics.framework/CoreGraphics"
		)
		self.app_services = ctypes.CDLL(
			"/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices"
		)

		class CGPoint(ctypes.Structure):
			_fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]

		self.CGPoint = CGPoint

		self.cg.CGEventCreate.argtypes = [ctypes.c_void_p]
		self.cg.CGEventCreate.restype = ctypes.c_void_p

		self.cg.CGEventGetLocation.argtypes = [ctypes.c_void_p]
		self.cg.CGEventGetLocation.restype = self.CGPoint

		self.cg.CGEventCreateMouseEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint32, self.CGPoint, ctypes.c_uint32]
		self.cg.CGEventCreateMouseEvent.restype = ctypes.c_void_p

		self.cg.CGEventSetType.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
		self.cg.CGEventSetType.restype = None

		self.cg.CGEventSetLocation.argtypes = [ctypes.c_void_p, self.CGPoint]
		self.cg.CGEventSetLocation.restype = None

		self.cg.CGEventPost.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
		self.cg.CGEventPost.restype = None

		self.cg.CFWarpsMouse = getattr(self.cg, "CGWarpMouseCursorPosition")
		self.cg.CFWarpsMouse.argtypes = [self.CGPoint]
		self.cg.CFWarpsMouse.restype = None

		try:
			self.cg.CGAssociateMouseAndMouseCursorPosition.argtypes = [ctypes.c_bool]
			self.cg.CGAssociateMouseAndMouseCursorPosition.restype = ctypes.c_int
		except AttributeError:
			self.cg.CGAssociateMouseAndMouseCursorPosition = None

		self.cg.CFRelease.argtypes = [ctypes.c_void_p]
		self.cg.CFRelease.restype = None

		try:
			self.app_services.AXIsProcessTrustedWithOptions.argtypes = [ctypes.c_void_p]
			self.app_services.AXIsProcessTrustedWithOptions.restype = ctypes.c_bool
		except AttributeError:
			self.app_services.AXIsProcessTrustedWithOptions = None

	def is_accessibility_trusted(self) -> bool:
		if not self.app_services.AXIsProcessTrustedWithOptions:
			return True
		try:
			return bool(self.app_services.AXIsProcessTrustedWithOptions(None))
		except Exception:
			return True

	def get_mouse_location(self):
		event_ref = self.cg.CGEventCreate(None)
		try:
			loc = self.cg.CGEventGetLocation(event_ref)
			return (loc.x, loc.y)
		finally:
			self.cg.CFRelease(event_ref)

	def post_mouse_move(self, x, y):
		point = self.CGPoint(x, y)
		event_ref = self.cg.CGEventCreateMouseEvent(None, kCGEventMouseMoved, point, kCGMouseButtonLeft)
		try:
			self.cg.CGEventSetType(event_ref, kCGEventMouseMoved)
			self.cg.CGEventSetLocation(event_ref, point)
			self.cg.CGEventPost(kCGHIDEventTap, event_ref)
		finally:
			self.cg.CFRelease(event_ref)

	def warp_mouse(self, x, y):
		if self.cg.CGAssociateMouseAndMouseCursorPosition:
			try:
				self.cg.CGAssociateMouseAndMouseCursorPosition(True)
			except Exception:
				pass
		self.cg.CFWarpsMouse(self.CGPoint(x, y))



def jiggle_loop(interval_seconds: float = 0.8, pixel_delta: int = 15):
	cg = CoreGraphics()

	def handle_sigint(signum, frame):
		print("\nStopping mouse jiggler...", flush=True)
		sys.exit(0)

	signal.signal(signal.SIGINT, handle_sigint)
	signal.signal(signal.SIGTERM, handle_sigint)

	if not cg.is_accessibility_trusted():
		print(
			"Accessibility permissions are not granted. Enable them in System Settings → Privacy & Security → Accessibility for your terminal/IDE.",
			file=sys.stderr,
			flush=True,
		)

	print(
		f"Mouse jiggler started: every {interval_seconds:.1f}s move {pixel_delta} px. Press Ctrl+C to stop.",
		flush=True,
	)

	use_warp = False
	try:
		x0, y0 = cg.get_mouse_location()
		cg.post_mouse_move(x0 + 1, y0)
		cg.post_mouse_move(x0, y0)
	except Exception:
		use_warp = True

	if use_warp:
		print("Using CGWarpMouseCursorPosition fallback.", flush=True)
	else:
		print("Using CGEventPost for mouse move.", flush=True)

	direction = 1
	axis_is_x = True

	while True:
		try:
			x_before, y_before = cg.get_mouse_location()
			if use_warp:
				if axis_is_x:
					cg.warp_mouse(x_before + direction * pixel_delta, y_before)
				else:
					cg.warp_mouse(x_before, y_before + direction * pixel_delta)
				x_after, y_after = cg.get_mouse_location()
				if x_after == x_before and y_after == y_before:
					axis_is_x = not axis_is_x
				else:
					cg.warp_mouse(x_before, y_before)
			else:
				if axis_is_x:
					cg.post_mouse_move(x_before + direction * pixel_delta, y_before)
					cg.post_mouse_move(x_before, y_before)
				else:
					cg.post_mouse_move(x_before, y_before + direction * pixel_delta)
					cg.post_mouse_move(x_before, y_before)
			direction *= -1
		except Exception as exc:
			print(
				"Warning: failed to move mouse. Ensure terminal/IDE has Accessibility permissions (System Settings → Privacy & Security → Accessibility).",
				file=sys.stderr,
				flush=True,
			)
			print(f"Details: {exc}", file=sys.stderr, flush=True)
			use_warp = True

		time.sleep(interval_seconds)


if __name__ == "__main__":
	jiggle_loop(interval_seconds=0.8, pixel_delta=15)
