# SPDX-FileCopyrightText: 2009-2023 Blender Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
from bpy.types import Panel, Menu, UIList
from rna_prop_ui import PropertyPanel

from bl_ui.properties_animviz import (
    MotionPathButtonsPanel,
    MotionPathButtonsPanel_display,
)


class ArmatureButtonsPanel:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.armature


class DATA_PT_context_arm(ArmatureButtonsPanel, Panel):
    bl_label = ""
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout

        ob = context.object
        arm = context.armature
        space = context.space_data

        if ob:
            layout.template_ID(ob, "data")
        elif arm:
            layout.template_ID(space, "pin_id")


class DATA_PT_pose(ArmatureButtonsPanel, Panel):
    bl_label = "Pose"

    def draw(self, context):
        layout = self.layout

        arm = context.armature

        layout.row().prop(arm, "pose_position", expand=True)


class DATA_PT_display(ArmatureButtonsPanel, Panel):
    bl_label = "Viewport Display"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        ob = context.object
        arm = context.armature

        layout.prop(arm, "display_type", text="Display As")

        col = layout.column(align=True)
        col.label( text = "Show")
        col.use_property_split = False
        row = col.row()
        row.separator()
        row.prop(arm, "show_names", text="Names")
        row.prop_decorator(arm, "show_names")
        row = col.row()
        row.separator()
        row.prop(arm, "show_bone_custom_shapes", text="Shapes")
        row.prop_decorator(arm, "show_bone_custom_shapes")
        row = col.row()
        row.separator()
        row.prop(arm, "show_bone_colors", text="Bone Colors")
        row.prop_decorator(arm, "show_bone_colors")

        if ob:
            row = col.row()
            row.separator()
            row.prop(ob, "show_in_front", text="In Front")
            row.prop_decorator(ob, "show_in_front")

        split = col.split(factor = 0.38)
        col = split.column()
        col.use_property_split = False
        row = col.row()
        row.separator()
        row.prop(arm, "show_axes", text="Axes")
        col = split.column()
        if arm.show_axes:
            row = col.row()
            row.use_property_split = False
            row.prop(arm, "axes_position", text="")

        else:
            row = col.row()
            row.label(icon='DISCLOSURE_TRI_RIGHT')
        subrow = row.row()
        subrow.alignment='RIGHT'
        subrow.prop_decorator(arm, "show_axes")

        sub = col.row(align=True)
        sub.prop(arm, "relation_line_position", text="Relations", expand=True)


class DATA_UL_bone_collections(UIList):
    def draw_item(self, _context, layout, armature, bcoll, _icon, _active_data, _active_propname, _index):
        active_bone = armature.edit_bones.active or armature.bones.active
        has_active_bone = active_bone and bcoll.name in active_bone.collections

        layout.prop(bcoll, "name", text="", emboss=False,
                    icon='DOT' if has_active_bone else 'BLANK1')

        if armature.override_library:
            icon = 'LIBRARY_DATA_OVERRIDE' if bcoll.is_local_override else 'BLANK1'
            layout.prop(
                bcoll,
                "is_local_override",
                text="",
                emboss=False,
                icon=icon)

        layout.prop(bcoll, "is_visible", text="", emboss=False,
                    icon='HIDE_OFF' if bcoll.is_visible else 'HIDE_ON')


class DATA_PT_bone_collections(ArmatureButtonsPanel, Panel):
    bl_label = "Bone Collections"

    def draw(self, context):
        layout = self.layout

        arm = context.armature
        active_bcoll = arm.collections.active

        row = layout.row()
        row.template_bone_collection_tree()

        col = row.column(align=True)
        col.operator("armature.collection_add", icon='ADD', text="")
        col.operator("armature.collection_remove", icon='REMOVE', text="")
        if active_bcoll:
            col.separator()
            col.operator("armature.collection_move", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("armature.collection_move", icon='TRIA_DOWN', text="").direction = 'DOWN'
            col.separator()

        col.menu("ARMATURE_MT_collection_context_menu", icon='DOWNARROW_HLT', text="")

        row = layout.row()

        sub = row.row(align=True)
        sub.operator("armature.collection_assign", icon='COLLECTION_BONE_ADD', text="Assign")
        sub.operator("armature.collection_unassign", icon='COLLECTION_BONE_REMOVE', text="Remove")

        sub = row.row(align=True)
        sub.operator("armature.collection_select", icon='RESTRICT_SELECT_OFF', text="Select")
        sub.operator("armature.collection_deselect", icon='SELECT_NONE', text="Deselect")


class ARMATURE_MT_collection_context_menu(Menu):
    bl_label = "Bone Collection Specials"

    def draw(self, context):
        layout = self.layout

        arm = context.armature
        active_bcoll = arm.collections.active

        active_bcoll_is_locked = arm.collections.active and not arm.collections.active.is_editable

        # The poll function doesn't have access to the parent index property, so
        # it cannot disable this operator depending on whether the parent is
        # editable or not. That means this menu has to do the disabling for it.
        sub = layout.column()
        sub.enabled = not active_bcoll_is_locked
        props = sub.operator(
            "armature.collection_add", text="Add Child Collection", icon="COLLECTION_NEW"
        )
        props.parent_index = arm.collections.active_index

        props = layout.operator("armature.collection_solo_visibility", icon='HIDE_UNSELECTED')
        props.name = active_bcoll.name if active_bcoll else ""
        layout.operator("armature.collection_show_all", icon='SHOW_UNSELECTED')


class ARMATURE_MT_collection_tree_context_menu(Menu):
    bl_label = "Bone Collections"

    def draw(self, context):
        layout = self.layout
        arm = context.armature

        active_bcoll_is_locked = arm.collections.active and not arm.collections.active.is_editable

        # The poll function doesn't have access to the parent index property, so
        # it cannot disable this operator depending on whether the parent is
        # editable or not. That means this menu has to do the disabling for it.
        sub = layout.column()
        sub.enabled = not active_bcoll_is_locked
        props = sub.operator(
            "armature.collection_add", text="Add Child Collection", icon="COLLECTION_NEW"
        )
        props.parent_index = arm.collections.active_index
        sub.operator("armature.collection_remove", icon="REMOVE")

        layout.separator()

        layout.operator("armature.collection_solo_visibility", icon="HIDE_UNSELECTED")
        layout.operator("armature.collection_show_all", icon="SHOW_UNSELECTED")

        layout.separator()

        # These operators can be used to assign to a named collection as well, and
        # don't necessarily always use the active bone collection. That means that
        # they have the same limitation as described above.
        sub = layout.column()
        sub.enabled = not active_bcoll_is_locked
        sub.operator("armature.collection_assign", text="Assign Selected Bones", icon="COLLECTION_BONE_ADD")
        sub.operator("armature.collection_unassign", text="Remove Selected Bones", icon="COLLECTION_BONE_REMOVE")

        layout.separator()

        layout.operator("armature.collection_select", text="Select Bones", icon="RESTRICT_SELECT_OFF")
        layout.operator("armature.collection_deselect", text="Deselect Bones", icon="SELECT_NONE")


class DATA_PT_iksolver_itasc(ArmatureButtonsPanel, Panel):
    bl_label = "Inverse Kinematics"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.pose

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        ob = context.object
        itasc = ob.pose.ik_param

        layout.prop(ob.pose, "ik_solver")

        if itasc:
            layout.prop(itasc, "mode")
            layout.prop(itasc, "translate_root_bones")
            simulation = (itasc.mode == 'SIMULATION')
            if simulation:
                layout.prop(itasc, "reiteration_method", expand=False)

            col = layout.column()
            col.active = not simulation or itasc.reiteration_method != 'NEVER'
            col.prop(itasc, "precision")
            col.prop(itasc, "iterations")

            col.prop(itasc, "solver")
            if simulation:
                col.prop(itasc, "feedback")
                col.prop(itasc, "velocity_max")
            if itasc.solver == 'DLS':
                col.separator()
                col.prop(itasc, "damping_max", text="Damping Max", slider=True)
                col.prop(itasc, "damping_epsilon", text="Damping Epsilon", slider=True)

            if simulation:
                col.use_property_split = False
                col.prop(itasc, "use_auto_step")
                col.use_property_split = True
                sub = layout.column(align=True)
                if itasc.use_auto_step:
                    sub.prop(itasc, "step_min", text="Steps Min")
                    sub.prop(itasc, "step_max", text="Max")
                else:
                    sub.prop(itasc, "step_count", text="Steps")


class DATA_PT_motion_paths(MotionPathButtonsPanel, Panel):
    # bl_label = "Bones Motion Paths"
    bl_options = {'DEFAULT_CLOSED'}
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        # XXX: include pose-mode check?
        return (context.object) and (context.armature)

    def draw(self, context):
        # layout = self.layout

        ob = context.object
        avs = ob.pose.animation_visualization

        pchan = context.active_pose_bone
        mpath = pchan.motion_path if pchan else None

        self.draw_settings(context, avs, mpath, bones=True)


class DATA_PT_motion_paths_display(MotionPathButtonsPanel_display, Panel):
    # bl_label = "Bones Motion Paths"
    bl_context = "data"
    bl_parent_id = "DATA_PT_motion_paths"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        # XXX: include pose-mode check?
        return (context.object) and (context.armature)

    def draw(self, context):
        # layout = self.layout

        ob = context.object
        avs = ob.pose.animation_visualization

        pchan = context.active_pose_bone
        mpath = pchan.motion_path if pchan else None

        self.draw_settings(context, avs, mpath, bones=True)


class DATA_PT_custom_props_arm(ArmatureButtonsPanel, PropertyPanel, Panel):
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}
    _context_path = "object.data"
    _property_type = bpy.types.Armature


class DATA_PT_custom_props_bcoll(ArmatureButtonsPanel, PropertyPanel, Panel):
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}
    _context_path = "armature.collections.active"
    _property_type = bpy.types.BoneCollection
    bl_parent_id = "DATA_PT_bone_collections"

    @classmethod
    def poll(cls, context):
        arm = context.armature
        if not arm:
            return False

        is_lib_override = arm.id_data.override_library and arm.id_data.override_library.reference
        if is_lib_override:
            # This is due to a limitation in scripts/modules/rna_prop_ui.py; if that
            # limitation is lifted, this poll function should be adjusted.
            return False

        return arm.collections.active


classes = (
    DATA_PT_context_arm,
    DATA_PT_pose,
    DATA_PT_bone_collections,
    DATA_UL_bone_collections,
    ARMATURE_MT_collection_context_menu,
    ARMATURE_MT_collection_tree_context_menu,
    DATA_PT_motion_paths,
    DATA_PT_motion_paths_display,
    DATA_PT_display,
    DATA_PT_iksolver_itasc,
    DATA_PT_custom_props_arm,
    DATA_PT_custom_props_bcoll,
)

if __name__ == "__main__":  # only for live edit.
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
