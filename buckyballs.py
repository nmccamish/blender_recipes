import addon_utils
import bpy

BUCKYBALL_NAME = "Buckyball"
CARBON_NAME = "Carbon"
SKELETON_NAME = "Skeleton"

CARBON_COLOR = (0, 0, 0, 0)
SKELETON_COLOR = (10, 10, 10, 0)


def check_tissue_addon():
    if addon_utils.check("bl_ext.blender_org.tissue") != (True, True):
        print("You need the Tissues extension installed, enabled, and loaded!")

        return False

    return True


def clear_all():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def activate_object(name):
    obj = bpy.context.scene.objects[name]

    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)


def create_material(name, base_color):
    mat = bpy.data.materials.new(name)

    node = mat.node_tree.nodes["Principled BSDF"]
    node.inputs["Base Color"].default_value = base_color

    return mat


def add_skeleton():
    bpy.ops.mesh.primitive_ico_sphere_add(calc_uvs=False, radius=1, subdivisions=2)
    # NOTE: outputs warning "Cannot move modifier beyond the start of the list"
    bpy.ops.object.dual_mesh()  # from Tissue addon

    obj = bpy.context.active_object
    obj.name = BUCKYBALL_NAME
    obj.data.name = SKELETON_NAME

    mod1 = obj.modifiers.new("Wireframe", "WIREFRAME")
    mod1.thickness = 0.06

    mod2 = obj.modifiers.new("Bevel", "BEVEL")
    mod2.segments = 2  # 1 or 2 works

    mat = create_material(SKELETON_NAME, SKELETON_COLOR)
    obj.data.materials.append(mat)

    bpy.ops.object.shade_smooth()


def add_carbon_atom():
    bpy.ops.mesh.primitive_ico_sphere_add(calc_uvs=False, radius=1, subdivisions=2)
    bpy.ops.object.shade_smooth()

    obj = bpy.context.active_object
    obj.name = CARBON_NAME

    mat = create_material(CARBON_NAME, CARBON_COLOR)
    obj.data.materials.append(mat)


def attach_carbon_atoms(skeleton_name=BUCKYBALL_NAME):
    activate_object(BUCKYBALL_NAME)

    bpy.ops.object.particle_system_add()

    obj = bpy.data.objects[BUCKYBALL_NAME]
    sys = obj.particle_systems[-1]
    part = bpy.data.particles[sys.settings.name]

    part.count = 80
    part.emit_from = "VERT"
    part.type = "HAIR"
    part.use_emit_random = False

    carbon_obj = bpy.data.objects[CARBON_NAME]
    part.render_type = "OBJECT"
    part.instance_object = carbon_obj
    part.particle_size = 0.02

    bpy.ops.object.modifier_move_to_index(modifier=sys.name, index=0)
    bpy.ops.object.duplicates_make_real(use_base_parent=True)
    bpy.data.objects.remove(carbon_obj, do_unlink=True)

    for mod in obj.modifiers:
        bpy.ops.object.modifier_apply(modifier=mod.name)

    bpy.ops.object.mode_set(mode="EDIT")

    group = bpy.context.object.vertex_groups.new()
    group.name = SKELETON_NAME

    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.object.vertex_group_assign()


if not check_tissue_addon():
    exit()

clear_all()
add_skeleton()
add_carbon_atom()
attach_carbon_atoms()
