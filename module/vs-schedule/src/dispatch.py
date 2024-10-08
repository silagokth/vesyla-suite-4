import os
import sys
import logging
import sync
import schedule
import generate
import parse
import codegen
import ds_pb2 as ds

# class EpochRegion:
#     def __init__(self, name, content):
#         self.name = name
#         self.content = content
#     def __str__(self):
#         return "EpochBlock: " + str(self.name)

# class LoopRegion:
#     def __init__(self, name, count, content):
#         self.name = name
#         self.count = count
#         self.content = content
#     def __str__(self):
#         return "LoopRegion " + str(self.name) + " " + str(self.count) + ": [ " + ", ".join([str(x) for x in self.content]) +" ]"

# class ProgramRegion:
#     def __init__(self, content):
#         self.content = content
#     def __str__(self):
#         return "ProgramRegion: [ "+", ".join([str(x) for x in self.content])+" ]"

# class CstrRegion:
#     def __init__(self, name, content):
#         self.name = name
#         self.content = content
#     def __str__(self):
#         return "CstrBlock: " + str(self.name)

# def parse_pasm(file_path):
#     epoch_region = pp.Group(pp.Forward("epoch")+pp.Word(pp.alphanums)+"{"+pp.SkipTo("}")+"}")
#     loop_region = pp.Group(pp.Forward("loop")+pp.Word(pp.alphanums)+pp.Word(pp.nums)+"{"+pp.Group(pp.OneOrMore(epoch_region))+"}")
#     program = pp.Group(pp.ZeroOrMore(epoch_region | loop_region))
#     program.ignore(pp.pythonStyleComment)
    
#     with open(file_path, "r") as file:
#         result = program.parseString(file.read())

#     return result

# def parse_cstr(file_path):
#     epoch_region = pp.Group(pp.Forward("epoch")+pp.Word(pp.alphanums)+"{"+pp.SkipTo("}")+"}")
#     program = pp.Group(pp.ZeroOrMore(epoch_region))
#     program.ignore(pp.pythonStyleComment)

#     with open(file_path, "r") as file:
#         result = program.parseString(file.read())

#     return result

# def analyze_block(block):
#     if block[0] == "epoch":
#         return EpochRegion(block[1], block[3])
#     elif block[0] == "loop":
#         block_list = []
#         for sub_block in block[4]:
#             block_list.append(analyze_block(sub_block))
#         return LoopRegion(block[1], block[2], block_list)
#     else:
#         logging.error("Unknown block type: %s", block[0])
#         sys.exit(1)

# def construct_ast(parsed_result):
#     ast = ProgramRegion([])
#     for block in parsed_result[0]:
#         ast.content.append(analyze_block(block))
#     return ast

# def construct_cstr_list(parsed_result):
#     cstr_list = []
#     for block in parsed_result[0]:
#         cstr_list.append(CstrRegion(block[1], block[3]))
#     return cstr_list

# def find_instruction_count(asm_txt):
#     instr_count = {}
#     curr_cell = None
#     for line in asm_txt.split("\n"):
#         # remove comments
#         line = re.sub(r'#.*$', '', line)
#         # remove leading and trailing whitespaces
#         line = line.strip()
#         # skip empty lines
#         if not line:
#             continue
#         pattern = re.compile(r'cell\s+(\d+_\d+)')
#         match = pattern.search(line)
#         if match:
#             cell = match.group(1)
#             if cell not in instr_count:
#                 instr_count[cell] = 0
#             curr_cell = cell
#         else:
#             instr_count[curr_cell] += 1
#     return instr_count

# def shift_loop_level(asm, shift_level):
#     new_asm = ""
#     for line in asm.split("\n"):
#         # remove comments
#         line = re.sub(r'#.*$', '', line)
#         # remove leading and trailing whitespaces
#         line = line.strip()
#         # skip empty lines
#         if not line:
#             continue
#         pattern = re.compile(r'looph\s+(.*)$')
#         match = pattern.search(line)
#         if match:
#             parameters = match.group(1).split(",")
#             for i in range(len(parameters)):
#                 parameter = parameters[i]
#                 key, value = parameter.split("=")
#                 if key.strip() == "id":
#                     loop_id = int(value) + shift_level
#                     parameters[i] = "id=%d" % loop_id
#                     break
#             new_asm += "looph " + ",".join(parameters) + "\n"
#             continue
#         pattern = re.compile(r'loopt\s+(.*)$')
#         match = pattern.search(line)
#         if match:
#             parameters = match.group(1).split(",")
#             for i in range(len(parameters)):
#                 parameter = parameters[i]
#                 key, value = parameter.split("=")
#                 if key.strip() == "id":
#                     loop_id = int(value) + shift_level
#                     parameters[i] = "id=%d" % loop_id
#                     break
#             new_asm += "loopt " + ",".join(parameters) + "\n"
#             continue
#         new_asm += line + "\n"
#     return new_asm

def instr_count_in_contents(asmprog, contents, cells):
    instr_count ={}
    for cell in cells:
        cell_label = f"{cell['x']}_{cell['y']}"
        instr_count[cell_label] = 0
    
    cell_label = None
    for content in contents:
        record = asmprog.records[content]
        if record.kind == ds.ASMRecord.Kind.CELL:
            cell_label = f"{record.parameters['x']}_{record.parameters['y']}"
        if record.kind == ds.ASMRecord.Kind.INSTR:
            if cell_label is not None:
                instr_count[cell_label] += 1
            else:
                logging.error("Instruction outside of cell")
                sys.exit(-1)
    
    return instr_count

def schedule_epoch(id, pasm_prog, cstr_prog, cells, output_dir):
    pasm_path = os.path.join(output_dir, "0.pasm")
    cstr_path = os.path.join(output_dir, "0.cstr")
    asm_path = os.path.join(output_dir, "0.asm")
    model_path = os.path.join(output_dir, "model.txt")
    timing_table_path = os.path.join(output_dir, "timing_table.json")
    with open(pasm_path, "w") as file:
        text = codegen.pasmrecord_to_text(id, pasm_prog)
        file.write(text)
    with open(cstr_path, "w") as file:
        text = codegen.cstrrecord_to_text(id, cstr_prog)
        file.write(text)
    generate.generate(pasm_path, cstr_path, output_dir)
    schedule.schedule(model_path, output_dir)

    cell_labels = []
    for cell in cells:
        cell_labels.append(f"{cell['x']}_{cell['y']}")

    sync.sync_resource(pasm_path, timing_table_path, cell_labels, output_dir)
    with open(asm_path, "r") as file:
        txt = file.read()
        asm_epoch = parse.text_to_asm_epoch(txt)
        return asm_epoch

def create_asm_for_region(id, pasmprog, cstrprog, cells, scalar_reg_counters, bool_reg_counters, output_dir, asmprog):
    MAX_SCALAR_REG = 15
    MAX_BOOL_REG = 15

    record = pasmprog.records[id]
    if record.kind == ds.PASMRecord.Kind.LOOP:
        record_id_vector = []

        iter = record.parameters["iter"]

        for cell in cells:
            cell_label = f"{cell['x']}_{cell['y']}"
            scalar_reg_counters[cell_label] += 1
            bool_reg_counters[cell_label] += 1

        loop_body_contents = []
        for content in record.contents:
            new_asmprog = ds.ASMProg()
            content_id_vector = create_asm_for_region(content, pasmprog, cstrprog, cells, scalar_reg_counters, bool_reg_counters, output_dir, new_asmprog)
            loop_body_contents.extend(content_id_vector)
            for record_id in content_id_vector:
                asmprog.records[record_id].CopyFrom(new_asmprog.records[record_id])

        for cell in cells:
            cell_label = f"{cell['x']}_{cell['y']}"
            scalar_reg_counters[cell_label] -= 1
            bool_reg_counters[cell_label] -= 1

        instr_count = instr_count_in_contents(asmprog, loop_body_contents, cells)

        for cell in cells:
            cell_label = f"{cell['x']}_{cell['y']}"

            curr_scalar_reg = MAX_SCALAR_REG - scalar_reg_counters[cell_label]
            curr_bool_reg = MAX_BOOL_REG - bool_reg_counters[cell_label]

            cell_record = ds.ASMRecord()
            cell_record.id = parse.get_random_id()
            cell_record.kind = ds.ASMRecord.Kind.CELL
            cell_record.parameters["x"] = cell['x']
            cell_record.parameters["y"] = cell['y']
            asmprog.records[cell_record.id].CopyFrom(cell_record)
            record_id_vector.append(cell_record.id)
            
            
            # iterator initialization
            # calc (mode=add, operand1=0, operand2_sd=s, operand_2=0, return=curr_scalar_reg)
            init_record = ds.ASMRecord()
            init_record.id = parse.get_random_id()
            init_record.kind = ds.ASMRecord.Kind.INSTR
            init_record.name = "calc"
            init_record.parameters["mode"] = "add"
            init_record.parameters["operand1"] = "0"
            init_record.parameters["operand2_sd"] = "s"
            init_record.parameters["operand2"] = "0"
            init_record.parameters["result"] = str(curr_scalar_reg)
            asmprog.records[init_record.id].CopyFrom(init_record)
            record_id_vector.append(init_record.id)

            # Compare
            # calc (mode=lt, operand1=reg_counter, operand2_sd=s, operand2=iter, return=curr_bool_reg)
            compare_record = ds.ASMRecord()
            compare_record.id = parse.get_random_id()
            compare_record.kind = ds.ASMRecord.Kind.INSTR
            compare_record.name = "calc"
            compare_record.parameters["mode"] = "lt"
            compare_record.parameters["operand1"] = str(curr_scalar_reg)
            compare_record.parameters["operand2_sd"] = "s"
            compare_record.parameters["operand2"] = iter
            compare_record.parameters["result"] = str(curr_bool_reg)
            asmprog.records[compare_record.id].CopyFrom(compare_record)
            record_id_vector.append(compare_record.id)

            # branch brn0
            # brn <loop_label_brn0> (reg=reg_counter, target_true=+1, target_false=brn1+1)
            branch_record = ds.ASMRecord()
            branch_record.id = parse.get_random_id()
            branch_record.kind = ds.ASMRecord.Kind.INSTR
            branch_record.name = "brn"
            branch_record.parameters["reg"] = str(curr_bool_reg)
            branch_record.parameters["target_true"] = "1"
            branch_record.parameters["target_false"] = str(instr_count[cell_label] + 3)
            asmprog.records[branch_record.id].CopyFrom(branch_record)
            record_id_vector.append(branch_record.id)

        #loop body
        for content in loop_body_contents:
            record_id_vector.append(content)
            
        for cell in cells:
            cell_label = f"{cell['x']}_{cell['y']}"

            # Cell record
            cell_record = ds.ASMRecord()
            cell_record.id = parse.get_random_id()
            cell_record.kind = ds.ASMRecord.Kind.CELL
            cell_record.parameters["x"] = cell['x']
            cell_record.parameters["y"] = cell['y']
            asmprog.records[cell_record.id].CopyFrom(cell_record)
            record_id_vector.append(cell_record.id)

            # increment
            # calc (mode=add, operand1=curr_scalar_reg, operand2_sd=s, operand1=2, return=curr_scalar_reg)
            increment_record = ds.ASMRecord()
            increment_record.id = parse.get_random_id()
            increment_record.kind = ds.ASMRecord.Kind.INSTR
            increment_record.name = "calc"
            increment_record.parameters["mode"] = "add"
            increment_record.parameters["operand1"] = str(curr_scalar_reg)
            increment_record.parameters["operand2_sd"] = "s"
            increment_record.parameters["operand2"] = "1"
            increment_record.parameters["result"] = str(curr_scalar_reg)
            asmprog.records[increment_record.id].CopyFrom(increment_record)
            record_id_vector.append(increment_record.id)

            # branch brn1
            # brn <loop_label_brn1> (target_true=target_false=cmp)
            branch_record = ds.ASMRecord()
            branch_record.id = parse.get_random_id()
            branch_record.kind = ds.ASMRecord.Kind.INSTR
            branch_record.name = "brn"
            branch_record.parameters["target_true"] = str(-instr_count[cell_label] - 3)
            branch_record.parameters["target_false"] = str(-instr_count[cell_label] - 3)
            asmprog.records[branch_record.id].CopyFrom(branch_record)
            record_id_vector.append(branch_record.id)

        return record_id_vector
    elif record.kind == ds.PASMRecord.Kind.COND:
        # TODO: make it timing balanced condition.
        record_id_vector = []
        reg = record.parameters["reg"]
        x = record.parameters["x"]
        y = record.parameters["y"]
        cell_label = f"{x}_{y}"

        new_cells = [{"x": x, "y": y}]
        cond_body_contents = []
        for content in record.contents:
            new_asmprog = ds.ASMProg()
            content_id_vector = create_asm_for_region(content, pasmprog, cstrprog, new_cells, scalar_reg_counters, bool_reg_counters, output_dir, new_asmprog)
            cond_body_contents.extend(content_id_vector)
            for record_id in content_id_vector:
                asmprog.records[record_id].CopyFrom(new_asmprog.records[record_id])

        instr_count = instr_count_in_contents(asmprog, cond_body_contents, new_cells)

        cell_record = ds.ASMRecord()
        cell_record.id = "cond_cell"
        cell_record.kind = ds.ASMRecord.Kind.CELL
        cell_record.parameters["x"] = x
        cell_record.parameters["y"] = y
        asmprog.records[cell_record.id].CopyFrom(cell_record)
        record_id_vector.append(cell_record.id)

        # branch brn0
        # brn <cond_label_brn0> (reg=reg, target_true=end+1, target_false=+1)
        branch_record = ds.ASMRecord()
        branch_record.id = "cond_branch"
        branch_record.kind = ds.ASMRecord.Kind.INSTR
        branch_record.name = "brn"
        branch_record.parameters["reg"] = reg
        branch_record.parameters["target_true"] = str(instr_count[cell_label] + 1)
        branch_record.parameters["target_false"] = "1"
        asmprog.records[branch_record.id].CopyFrom(branch_record)
        record_id_vector.append(branch_record.id)

        for content in cond_body_contents:
            record_id_vector.append(content)
        
        return record_id_vector
    
    elif record.kind == ds.PASMRecord.Kind.EPOCH:

        # scan through the contents to get the count of raw regions, cop regions and rop regions
        raw_region = 0
        cop_region = 0
        rop_region = 0
        for content in record.contents:
            cell_record = pasmprog.records[content]
            if cell_record.kind != ds.PASMRecord.Kind.CELL:
                logging.error("Expected CELL record, got %s", cell_record.kind)
                sys.exit(1)
            for sub_content in cell_record.contents:
                sub_record = pasmprog.records[sub_content]
                if sub_record.kind == ds.PASMRecord.Kind.RAW:
                    raw_region += 1
                elif sub_record.kind == ds.PASMRecord.Kind.COP:
                    cop_region += 1
                elif sub_record.kind == ds.PASMRecord.Kind.ROP:
                    rop_region += 1
                else:
                    logging.error("Illegal record kind: %s", sub_record.kind)
                    sys.exit(-1)
        
        if raw_region > 0 and cop_region ==0 and rop_region == 0:
            # don't schedule this epoch region
            record_id_vector = []
            for content in record.contents:
                cell_record = pasmprog.records[content]
                cell_asmrecord = ds.ASMRecord()
                cell_asmrecord.id = parse.get_random_id()
                cell_asmrecord.kind = ds.ASMRecord.Kind.CELL
                cell_asmrecord.parameters.update(cell_record.parameters)
                asmprog.records[cell_asmrecord.id].CopyFrom(cell_asmrecord)
                record_id_vector.append(cell_asmrecord.id)
                
                for sub_content in cell_record.contents:
                    sub_record = pasmprog.records[sub_content]
                    for instr_content in sub_record.contents:
                        instr_record = pasmprog.records[instr_content]
                        instr_asmrecord = ds.ASMRecord()
                        instr_asmrecord.id = parse.get_random_id()
                        instr_asmrecord.kind = ds.ASMRecord.Kind.INSTR
                        instr_asmrecord.name = instr_record.name
                        instr_asmrecord.parameters.update(instr_record.parameters)
                        asmprog.records[instr_asmrecord.id].CopyFrom(instr_asmrecord)
                        record_id_vector.append(instr_asmrecord.id)
            return record_id_vector
        elif raw_region == 0:
            # schedule the epoch region
            workdir = os.path.join(output_dir, record.id)
            os.makedirs(workdir, exist_ok=True)
            asm_epoch = schedule_epoch(record.id, pasmprog, cstrprog, cells, workdir)
            record_id_vector = asm_epoch.contents
            
            for record_id in record_id_vector:
                asmprog.records[record_id].CopyFrom(asm_epoch.records[record_id])

            return record_id_vector
        else:
            logging.error("RAW region cannot be mixed with COP or ROP regions in the same epoch: ", record.id)
            sys.exit(-1)
    
    else:
        logging.error("Illegal record kind: %s", record.kind)
        sys.exit(-1)
    

def create_asm(pasmprog, cstrprog, cells, output_dir):
    record = pasmprog.records[pasmprog.start]
    if record.kind != ds.PASMRecord.Kind.START:
        logging.error("Expected START record, got %s", record.kind)
        sys.exit(1)
    
    asmprog = ds.ASMProg()
    scalar_reg_counters = {}
    bool_reg_counters = {}
    for cell in cells:
        cell_label = f"{cell['x']}_{cell['y']}"
        scalar_reg_counters[cell_label] = 0
        bool_reg_counters[cell_label] = 0

    for content in record.contents:
        content_recoed_id_vector = create_asm_for_region(content, pasmprog, cstrprog, cells, scalar_reg_counters, bool_reg_counters, output_dir, asmprog)
        asmprog.contents.extend(content_recoed_id_vector)

    return asmprog


    # if isinstance(block, EpochRegion):
    #     # create a working directory, name it after the resource block
    #     os.makedirs(os.path.join(output_dir, block.name), exist_ok=True)
    #     # generate pasm file
    #     with open(os.path.join(output_dir, block.name, "0.pasm"), "w") as file:
    #         file.write(block.content)
    #     # generate cstr file
    #     with open(os.path.join(output_dir, block.name, "0.cstr"), "w") as file:
    #         for cstr_block in cstr_list:
    #             if cstr_block.name == block.name:
    #                 file.write(cstr_block.content)
    #                 break
    #     # generate model
    #     generate.generate(os.path.join(output_dir, block.name, "0.pasm"), os.path.join(output_dir, block.name, "0.cstr"), os.path.join(output_dir, block.name))
    #     schedule.schedule(os.path.join(output_dir, block.name, "model.txt"), os.path.join(output_dir, block.name))
    #     sync.sync_resource(os.path.join(output_dir, block.name, "0.pasm"), os.path.join(os.path.join(output_dir, block.name), "timing_table.json"), cells, os.path.join(output_dir, block.name))
    #     with open(os.path.join(output_dir, block.name, "instr_lists.txt"), "r") as file:
    #         return file.read()
    # elif isinstance(block, LoopRegion):
    #     txt = ""
    #     for cell in cells:
    #         txt += "cell %s\n" % cell
    #         txt += "looph id=%d, iter=%s\n" % (loop_id_counter, block.count)

    #     asm_txt = ""
    #     for sub_block in block.content:
    #         asm_txt += schedule_block(sub_block, cstr_list, cells, loop_id_counter+1, os.path.join(output_dir, block.name))
    #     # find how many instructions are in the sub_block for each cell
    #     instr_count = find_instruction_count(asm_txt)
    #     for cell in cells:
    #         if cell not in instr_count:
    #             instr_count[cell] = 0
    #     asm_txt = shift_loop_level(asm_txt, 1)
    #     txt += asm_txt

    #     for cell in cells:
    #         txt += "cell %s\n" % cell
    #         txt += "loopt id=%d, pc=%d\n" % (loop_id_counter, -(instr_count[cell]))
    #     return txt
    # elif isinstance(block, ProgramRegion):
    #     txt = ""
    #     for sub_block in block.content:
    #         txt += schedule_block(sub_block, cstr_list, cells, loop_id_counter, output_dir)
    #     return txt
    # else:
    #     logging.error("Unknown block type: %s", block)
    #     sys.exit(1)

def find_all_cells(pasmprog):
    cells = []
    cell_labels = set()
    for record_id in pasmprog.records:
        record = pasmprog.records[record_id]
        if record.kind == ds.PASMRecord.Kind.CELL:
            x = record.parameters["x"]
            y = record.parameters["y"]
            if f"{x}_{y}" not in cell_labels:
                cell_labels.add(f"{x}_{y}")
                cells.append({"x": x, "y": y})
    return cells

def optimize_asm(asmprog: ds.ASMProg):
    # place instruction of the same cell together
    cell_contents = {}
    curr_cell_label = None
    for id in asmprog.contents:
        record = asmprog.records[id]
        if record.kind == ds.ASMRecord.Kind.CELL:
            cell_label = f"{record.parameters['x']}_{record.parameters['y']}"
            if cell_label not in cell_contents:
                cell_contents[cell_label] = [id]
            curr_cell_label = cell_label
        else:
            if curr_cell_label is None:
                logging.error("Instruction outside of cell")
                sys.exit(-1)
            cell_contents[curr_cell_label].append(id)
    new_contents = []
    for cell_label in cell_contents:
        new_contents.extend(cell_contents[cell_label])
    asmprog.contents.clear()
    asmprog.contents.extend(new_contents)

def add_halt(asmprog, cells):
    for cell in cells:
        cell_record = ds.ASMRecord()
        cell_record.id = parse.get_random_id()
        cell_record.kind = ds.ASMRecord.Kind.CELL
        cell_record.parameters["x"] = cell["x"]
        cell_record.parameters["y"] = cell["y"]
        asmprog.records[cell_record.id].CopyFrom(cell_record)
        asmprog.contents.append(cell_record.id)
        halt_record = ds.ASMRecord()
        halt_record.id = parse.get_random_id()
        halt_record.kind = ds.ASMRecord.Kind.INSTR
        halt_record.name = "halt"
        asmprog.records[halt_record.id].CopyFrom(halt_record)
        asmprog.contents.append(halt_record.id)

def dispatch(file_pasm, file_cstr, output_dir):
    with open(file_pasm, "r") as file:
        pasmprog = parse.parse_pasm(file.read())
    with open(file_cstr, "r") as file:
        cstrprog = parse.parse_cstr(file.read())

    cells = find_all_cells(pasmprog)
    asmprog = create_asm(pasmprog, cstrprog, cells, output_dir)
    add_halt(asmprog, cells)
    optimize_asm(asmprog)

    txt = codegen.asmprog_to_text(asmprog)
    with open(os.path.join(output_dir, "0.asm"), "w") as file:
        file.write(txt)
