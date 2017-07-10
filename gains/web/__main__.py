from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from gains.web import app


app.run(debug=True, port=8000)
