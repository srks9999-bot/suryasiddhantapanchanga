"""
Debug context and tracing utilities for Panchanga calculations.

This module provides a context-based debugging system that captures
the control flow, function calls, and intermediate values during
panchanga calculations without requiring changes to function signatures.

Usage:
    from panchanga.core.debug_context import debug_context, debug_trace, debug_log

    # Enable debugging for a calculation
    with debug_context.enabled():
        result = some_calculation()
        traces = debug_context.get_traces()

    # Or use the decorator
    @debug_trace
    def my_function(x, y):
        debug_log("intermediate", value=x + y)
        return x * y
"""

import functools
import time
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from contextlib import contextmanager


@dataclass
class TraceEntry:
    """A single trace entry capturing a function call or log message."""
    timestamp: float
    sequence: int
    entry_type: str  # 'call', 'return', 'log', 'error'
    function_name: str
    module: str = ""
    args: Dict[str, Any] = field(default_factory=dict)
    result: Any = None
    message: str = ""
    depth: int = 0
    duration_ms: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        d = {
            'sequence': self.sequence,
            'type': self.entry_type,
            'function': self.function_name,
            'depth': self.depth,
        }
        if self.module:
            d['module'] = self.module
        if self.message:
            d['message'] = self.message
        if self.args:
            # Serialize args, handling non-JSON-serializable types
            d['args'] = {k: _safe_repr(v) for k, v in self.args.items()}
        if self.result is not None:
            d['result'] = _safe_repr(self.result)
        if self.duration_ms is not None:
            d['duration_ms'] = round(self.duration_ms, 3)
        return d


def _safe_repr(value: Any, max_len: int = 200) -> Any:
    """Safely convert a value to a JSON-serializable representation."""
    if value is None:
        return None
    if isinstance(value, (int, float, bool)):
        return value
    if isinstance(value, str):
        return value[:max_len] + '...' if len(value) > max_len else value
    if isinstance(value, (list, tuple)):
        if len(value) > 10:
            return f"[{type(value).__name__} with {len(value)} items]"
        return [_safe_repr(v, max_len) for v in value]
    if isinstance(value, dict):
        if len(value) > 10:
            return f"{{dict with {len(value)} keys}}"
        return {str(k): _safe_repr(v, max_len) for k, v in value.items()}
    # For other types, use repr with truncation
    r = repr(value)
    return r[:max_len] + '...' if len(r) > max_len else r


class DebugContext:
    """
    Context manager for debug tracing.
    
    Uses contextvars for thread-safe, async-safe context-local storage.
    """
    
    def __init__(self):
        self._enabled: ContextVar[bool] = ContextVar('debug_enabled', default=False)
        self._traces: ContextVar[List[TraceEntry]] = ContextVar('debug_traces', default=[])
        self._sequence: ContextVar[int] = ContextVar('debug_sequence', default=0)
        self._depth: ContextVar[int] = ContextVar('debug_depth', default=0)
        self._start_time: ContextVar[float] = ContextVar('debug_start_time', default=0.0)
    
    @property
    def is_enabled(self) -> bool:
        """Check if debug tracing is enabled."""
        return self._enabled.get()
    
    @contextmanager
    def enabled(self):
        """
        Context manager to enable debug tracing.
        
        Usage:
            with debug_context.enabled():
                # All traced functions will be captured
                result = calculate_panchanga(...)
                traces = debug_context.get_traces()
        """
        # Save current state
        old_enabled = self._enabled.get()
        old_traces = self._traces.get()
        old_sequence = self._sequence.get()
        old_depth = self._depth.get()
        
        # Initialize new debug session
        self._enabled.set(True)
        self._traces.set([])
        self._sequence.set(0)
        self._depth.set(0)
        self._start_time.set(time.perf_counter())
        
        try:
            yield self
        finally:
            # Restore previous state
            self._enabled.set(old_enabled)
            self._traces.set(old_traces)
            self._sequence.set(old_sequence)
            self._depth.set(old_depth)
    
    def _next_sequence(self) -> int:
        """Get next sequence number."""
        seq = self._sequence.get()
        self._sequence.set(seq + 1)
        return seq
    
    def _get_depth(self) -> int:
        """Get current call depth."""
        return self._depth.get()
    
    def _enter_call(self) -> int:
        """Enter a function call, increment depth."""
        depth = self._depth.get()
        self._depth.set(depth + 1)
        return depth
    
    def _exit_call(self):
        """Exit a function call, decrement depth."""
        depth = self._depth.get()
        self._depth.set(max(0, depth - 1))
    
    def add_trace(self, entry: TraceEntry):
        """Add a trace entry."""
        if self.is_enabled:
            traces = self._traces.get()
            traces.append(entry)
            self._traces.set(traces)
    
    def log(
        self,
        message: str,
        function_name: str = "",
        module: str = "",
        **kwargs
    ):
        """
        Add a log message to the trace.
        
        Args:
            message: Log message
            function_name: Name of the function (optional)
            module: Module name (optional)
            **kwargs: Additional values to log
        """
        if not self.is_enabled:
            return
        
        entry = TraceEntry(
            timestamp=time.perf_counter() - self._start_time.get(),
            sequence=self._next_sequence(),
            entry_type='log',
            function_name=function_name,
            module=module,
            message=message,
            args=kwargs,
            depth=self._get_depth()
        )
        self.add_trace(entry)
    
    def get_traces(self) -> List[Dict[str, Any]]:
        """Get all trace entries as dictionaries."""
        return [t.to_dict() for t in self._traces.get()]
    
    def get_trace_summary(self) -> Dict[str, Any]:
        """Get a summary of the trace."""
        traces = self._traces.get()
        
        # Count by type
        by_type = {}
        for t in traces:
            by_type[t.entry_type] = by_type.get(t.entry_type, 0) + 1
        
        # Get unique functions called
        functions_called = set()
        for t in traces:
            if t.entry_type == 'call' and t.function_name:
                functions_called.add(t.function_name)
        
        return {
            'total_entries': len(traces),
            'by_type': by_type,
            'functions_called': sorted(functions_called),
            'max_depth': max((t.depth for t in traces), default=0)
        }
    
    def format_trace_tree(self) -> str:
        """Format traces as an indented tree string."""
        lines = []
        for t in self._traces.get():
            indent = "  " * t.depth
            if t.entry_type == 'call':
                args_str = ", ".join(f"{k}={_safe_repr(v, 50)}" for k, v in t.args.items())
                lines.append(f"{indent}→ {t.function_name}({args_str})")
            elif t.entry_type == 'return':
                result_str = _safe_repr(t.result, 80)
                duration = f" [{t.duration_ms:.2f}ms]" if t.duration_ms else ""
                lines.append(f"{indent}← {t.function_name} = {result_str}{duration}")
            elif t.entry_type == 'log':
                args_str = ", ".join(f"{k}={_safe_repr(v, 50)}" for k, v in t.args.items())
                msg = f": {t.message}" if t.message else ""
                lines.append(f"{indent}  • {t.function_name}{msg} {args_str}")
            elif t.entry_type == 'error':
                lines.append(f"{indent}  ✗ ERROR in {t.function_name}: {t.message}")
        return "\n".join(lines)


# Global debug context instance
debug_context = DebugContext()


def debug_trace(func: Callable = None, *, name: str = None, log_args: bool = True, log_result: bool = True):
    """
    Decorator to trace function calls.
    
    Usage:
        @debug_trace
        def my_function(x, y):
            return x + y
        
        @debug_trace(name="custom_name", log_result=False)
        def another_function():
            pass
    """
    def decorator(fn):
        func_name = name or fn.__name__
        module_name = fn.__module__ if hasattr(fn, '__module__') else ""
        
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if not debug_context.is_enabled:
                return fn(*args, **kwargs)
            
            # Build args dict
            args_dict = {}
            if log_args:
                # Get parameter names if possible
                import inspect
                try:
                    sig = inspect.signature(fn)
                    params = list(sig.parameters.keys())
                    for i, arg in enumerate(args):
                        if i < len(params):
                            args_dict[params[i]] = arg
                        else:
                            args_dict[f'arg{i}'] = arg
                except (ValueError, TypeError):
                    for i, arg in enumerate(args):
                        args_dict[f'arg{i}'] = arg
                args_dict.update(kwargs)
            
            # Log call entry
            depth = debug_context._enter_call()
            start_time = time.perf_counter()
            
            call_entry = TraceEntry(
                timestamp=start_time - debug_context._start_time.get(),
                sequence=debug_context._next_sequence(),
                entry_type='call',
                function_name=func_name,
                module=module_name,
                args=args_dict,
                depth=depth
            )
            debug_context.add_trace(call_entry)
            
            try:
                result = fn(*args, **kwargs)
                
                # Log return
                if log_result:
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    return_entry = TraceEntry(
                        timestamp=time.perf_counter() - debug_context._start_time.get(),
                        sequence=debug_context._next_sequence(),
                        entry_type='return',
                        function_name=func_name,
                        module=module_name,
                        result=result,
                        depth=depth,
                        duration_ms=duration_ms
                    )
                    debug_context.add_trace(return_entry)
                
                return result
                
            except Exception as e:
                # Log error
                error_entry = TraceEntry(
                    timestamp=time.perf_counter() - debug_context._start_time.get(),
                    sequence=debug_context._next_sequence(),
                    entry_type='error',
                    function_name=func_name,
                    module=module_name,
                    message=str(e),
                    depth=depth
                )
                debug_context.add_trace(error_entry)
                raise
            finally:
                debug_context._exit_call()
        
        return wrapper
    
    if func is not None:
        # Called without parentheses: @debug_trace
        return decorator(func)
    else:
        # Called with parentheses: @debug_trace(...)
        return decorator


def debug_log(message: str, **kwargs):
    """
    Log a message to the debug trace.
    
    Usage:
        debug_log("Computing elongation", sun=sun_long, moon=moon_long)
    """
    if debug_context.is_enabled:
        # Try to get caller function name
        import inspect
        frame = inspect.currentframe()
        caller_name = ""
        module_name = ""
        if frame and frame.f_back:
            caller_name = frame.f_back.f_code.co_name
            module_name = frame.f_back.f_globals.get('__name__', '')
        
        debug_context.log(
            message=message,
            function_name=caller_name,
            module=module_name,
            **kwargs
        )


def debug_value(name: str, value: Any, description: str = ""):
    """
    Log a computed value with optional description.
    
    Usage:
        debug_value("mean_sun_longitude", mslong, "Mean solar longitude at sunrise")
    """
    if debug_context.is_enabled:
        import inspect
        frame = inspect.currentframe()
        caller_name = ""
        if frame and frame.f_back:
            caller_name = frame.f_back.f_code.co_name
        
        debug_context.log(
            message=description or f"Computed {name}",
            function_name=caller_name,
            **{name: value}
        )
