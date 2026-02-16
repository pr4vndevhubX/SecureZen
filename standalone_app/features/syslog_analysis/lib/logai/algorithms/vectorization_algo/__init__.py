#
# Copyright (c) 2023 Salesforce.com, inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
#
#
try:
    from .fasttext import FastText
except ImportError:
    pass

try:
    from .semantic import Semantic
except ImportError:
    pass

from .sequential import Sequential
from .tfidf import TfIdf

try:
    from .word2vec import Word2Vec
except ImportError:
    pass

from logai.utils.misc import is_torch_available, \
    is_transformers_available

_MODULES = [
    "Sequential",
    "TfIdf",
]

# Add others if they were successfully imported
if 'FastText' in locals(): _MODULES.append("FastText")
if 'Semantic' in locals(): _MODULES.append("Semantic")
if 'Word2Vec' in locals(): _MODULES.append("Word2Vec")

if is_torch_available() and is_transformers_available():
    from .forecast_nn import ForecastNN
    from .logbert import LogBERT

    _MODULES += [
        "ForecastNN",
        "LogBERT"
    ]

__all__ = _MODULES
