import asyncio

# Buffer settings
BUFFER_SIZE = 20
LOW_WATER_MARK = 5

# In-memory buffers per subject
QUESTION_BUFFER = {}

# One lock per subject
BUFFER_LOCKS = {}


def ensure_subject(subject: str):
    if subject not in QUESTION_BUFFER:
        QUESTION_BUFFER[subject] = []
        BUFFER_LOCKS[subject] = asyncio.Lock()


async def refill_buffer(subject: str, generate_fn):
    """
    Background task to refill buffer
    """
    ensure_subject(subject)

    async with BUFFER_LOCKS[subject]:
        if len(QUESTION_BUFFER[subject]) >= BUFFER_SIZE:
            return

        questions = await generate_fn(subject)

        if questions and isinstance(questions, list):
            QUESTION_BUFFER[subject].extend(questions)
