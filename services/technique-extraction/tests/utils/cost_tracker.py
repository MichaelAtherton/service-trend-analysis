"""
OpenAI API cost tracking for test suite execution.

Tracks and reports:
- Total API calls made during testing
- Input and output tokens consumed
- Estimated cost based on gpt-4o-mini pricing
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# Pricing as of November 2024 for gpt-4o-mini
GPT4O_MINI_INPUT_COST_PER_1K = 0.00015  # $0.150 per 1M tokens
GPT4O_MINI_OUTPUT_COST_PER_1K = 0.0006  # $0.600 per 1M tokens


@dataclass
class APICallRecord:
    """Record of a single OpenAI API call."""
    
    timestamp: datetime
    model: str
    input_tokens: int
    output_tokens: int
    estimated_cost: float
    endpoint: str = "chat_completion"
    

@dataclass
class CostTracker:
    """Tracks OpenAI API usage and costs across test suite execution."""
    
    suite_run_id: str
    start_time: datetime = field(default_factory=datetime.now)
    calls: list[APICallRecord] = field(default_factory=list)
    
    def record_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        endpoint: str = "chat_completion",
    ) -> None:
        """
        Record a single API call with token usage.
        
        Args:
            model: Model used (e.g., "gpt-4o-mini")
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            endpoint: API endpoint used
        """
        # Calculate cost based on gpt-4o-mini pricing
        input_cost = (input_tokens / 1000) * GPT4O_MINI_INPUT_COST_PER_1K
        output_cost = (output_tokens / 1000) * GPT4O_MINI_OUTPUT_COST_PER_1K
        total_cost = input_cost + output_cost
        
        record = APICallRecord(
            timestamp=datetime.now(),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost=total_cost,
            endpoint=endpoint,
        )
        
        self.calls.append(record)
    
    @property
    def total_calls(self) -> int:
        """Return total number of API calls made."""
        return len(self.calls)
    
    @property
    def total_input_tokens(self) -> int:
        """Return total input tokens consumed."""
        return sum(call.input_tokens for call in self.calls)
    
    @property
    def total_output_tokens(self) -> int:
        """Return total output tokens consumed."""
        return sum(call.output_tokens for call in self.calls)
    
    @property
    def total_tokens(self) -> int:
        """Return total tokens (input + output) consumed."""
        return self.total_input_tokens + self.total_output_tokens
    
    @property
    def total_cost(self) -> float:
        """Return total estimated cost in USD."""
        return sum(call.estimated_cost for call in self.calls)
    
    def get_summary(self) -> dict:
        """
        Get cost tracking summary for reporting.
        
        Returns:
            dict: Summary with total calls, tokens, and cost
        """
        return {
            "suite_run_id": self.suite_run_id,
            "start_time": self.start_time.isoformat(),
            "total_calls": self.total_calls,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost_usd": round(self.total_cost, 4),
        }
    
    def print_summary(self) -> None:
        """Print cost tracking summary to console."""
        summary = self.get_summary()
        
        print("\n" + "=" * 60)
        print("OpenAI API Cost Tracking Summary")
        print("=" * 60)
        print(f"Suite Run ID: {summary['suite_run_id']}")
        print(f"Start Time: {summary['start_time']}")
        print(f"Total API Calls: {summary['total_calls']}")
        print(f"Total Input Tokens: {summary['total_input_tokens']:,}")
        print(f"Total Output Tokens: {summary['total_output_tokens']:,}")
        print(f"Total Tokens: {summary['total_tokens']:,}")
        print(f"Estimated Cost: ${summary['estimated_cost_usd']:.4f} USD")
        print("=" * 60)
        print(f"Note: Pricing based on gpt-4o-mini rates")
        print(f"  - Input: ${GPT4O_MINI_INPUT_COST_PER_1K * 1000:.3f} per 1M tokens")
        print(f"  - Output: ${GPT4O_MINI_OUTPUT_COST_PER_1K * 1000:.3f} per 1M tokens")
        print("=" * 60 + "\n")

