import os
import pygame


def load_animation_sprites(path, name, frames):
    img = []
    for i in range(frames):
        path_name = os.path.join(path, str(name)+str(i + 1) + ".png")
        img.append(pygame.image.load(path_name))
    return img


def approach(val, target, step):
    if val > target:
        if val - step < target:
            return target
        else:
            return val - step
    else:
        if val + step > target:
            return target
        else:
            return val + step


def rot_center(image, angle, x, y):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(center=(x, y)).center)

    return rotated_image, new_rect


def outside_surface(surface, obj):
    w, h = surface.get_size()
    hb = obj.hitbox_rect
    if hb[0] > w or hb[0]+hb[2] < 0 or hb[1] > h or hb[1]+hb[3] < 0:
        return True
    return False


def test_approach():
    assert approach(10, 20, 2) == 10 + 2
    assert approach(10, 11, 2) == 11
    assert approach(10, 8, 3) == 8
    assert approach(10, 1, 3) == 10 - 3


def test_load_animation_sprites():
    frames = 5
    for i in range(frames):
        assert len(load_animation_sprites("starcall/assets/enemies/EyeBat", "EyeBat", i+1)) == i+1
