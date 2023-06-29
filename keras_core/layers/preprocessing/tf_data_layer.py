from tensorflow import nest

from keras_core import backend
from keras_core.api_export import keras_core_export
from keras_core.layers.layer import Layer
from keras_core.utils import backend_utils


@keras_core_export("keras_core.layers.TFDataLayer")
class TFDataLayer(Layer):
    """Layer that can safely used in a tf.data pipeline.

    The `call()` method must solely rely on `self.backend` ops.

    Only supports a single input tensor argument.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.backend = backend_utils.DynamicBackend()
        self._allow_non_tensor_positional_args = True

    def __call__(self, inputs, **kwargs):
        if backend_utils.in_tf_graph() and not isinstance(
            inputs, backend.KerasTensor
        ):
            # We're in a TF graph, e.g. a tf.data pipeline.
            self.backend.set_backend("tensorflow")
            inputs = nest.map_structure(
                lambda x: self.backend.convert_to_tensor(
                    x, dtype=self.compute_dtype
                ),
                inputs,
            )
            switch_convert_input_args = False
            if self._convert_input_args:
                self._convert_input_args = False
                switch_convert_input_args = True
            try:
                outputs = super().__call__(inputs, **kwargs)
            finally:
                self.backend.reset()
                if switch_convert_input_args:
                    self._convert_input_args = True
            return outputs
        return super().__call__(inputs, **kwargs)
