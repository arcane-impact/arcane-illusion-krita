from krita import DockWidgetFactoryBase, DockWidgetFactory
from .extension import ArcaneIllusion
from .image_generation import ImageGeneration
from .segmentation_palette import SegmentationPalette

krita = Krita.instance()
krita.addExtension(ArcaneIllusion(parent=krita))
krita.addDockWidgetFactory(
    DockWidgetFactory(
        ImageGeneration.id,
        DockWidgetFactoryBase.DockLeft,
        ImageGeneration,
    )
)
krita.addDockWidgetFactory(
    DockWidgetFactory(
        SegmentationPalette.id,
        DockWidgetFactoryBase.DockRight,
        SegmentationPalette,
    )
)
