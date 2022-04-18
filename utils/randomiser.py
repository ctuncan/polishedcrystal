#!/usr/bin/env python3

import sys
import random
import pathlib
import argparse


grass_encounters = []


def rom_addr(bank_addr):
    bank, addr = [int(x, 16) for x in bank_addr.split(":")]
    if bank > 0:
        bank -= 1
    return bank * 0x4000 + addr


def get_grass_wildmon(rom, addr):
    # Note to self, grass wildmons =
    # 2 bytes map id
    # 3 bytes rates
    # 3 (morn/day/nite) * 7 (pokemon) *
    # 1 byte level
    # 2 bytes pokemon
    pkmns = []
    addr += 5  # Skip map_id + rates
    for i in range(3 * 7):
        level = addr + 3 * i
        pkmn = level + 1
        pkmns.append(rom[pkmn : pkmn + 2])
    return pkmns


def set_grass_wildmon(rom, addr, pkmns):
    addr += 5  # Skip map_id + rates
    for i, new_pkmn in zip(range(3 * 7), pkmns):
        level = addr + 3 * i
        pkmn = level + 1
        rom[pkmn : pkmn + 2] = new_pkmn


def randomise(rom, sym):
    for line in open(sym):
        if line.startswith(";"):
            continue
        bank_addr, sym = line.split()
        if "._def_grass_wildmons_" in sym:
            grass_encounters.append((bank_addr, sym))

    rom_f = bytearray(open(rom, "r+b").read())

    grass = dict()
    for addr, sym in grass_encounters:
        addr = rom_addr(addr)
        grass[sym] = get_grass_wildmon(rom_f, addr)

    shuffled = list(grass.values())
    random.shuffle(shuffled)

    for (addr, sym), pkmn in zip(grass_encounters, shuffled):
        addr = rom_addr(addr)
        set_grass_wildmon(rom_f, addr, pkmn)

    with open(rom.with_suffix(".random.gbc"), "wb") as f:
        f.write(rom_f)


def cli_parser():
    parser = argparse.ArgumentParser(description="Randomise a polished crystal rom")

    parser.add_argument("rom", type=pathlib.Path)
    parser.add_argument("--symfile", type=pathlib.Path)

    return parser


def main():
    args = cli_parser().parse_args()

    if args.symfile is None:
        args.symfile = args.rom.with_suffix(".sym")

    randomise(args.rom, args.symfile)


if __name__ == "__main__":
    main()
