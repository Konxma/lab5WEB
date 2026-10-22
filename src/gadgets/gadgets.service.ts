import { Injectable, Logger, NotFoundException, OnModuleInit } from '@nestjs/common';
import { SlugService } from '../shared/slug.service';
import { GadgetEntity } from './gadget.entity';
import { CreateGadgetDto } from './dto/create-gadget.dto';
import { UpdateGadgetDto } from './dto/update-gadget.dto';

@Injectable()
export class GadgetsService implements OnModuleInit {
  private readonly logger = new Logger(GadgetsService.name);
  private readonly gadgets: GadgetEntity[] = [];
  private nextId = 1;

  constructor(private readonly slugService: SlugService) {}

  onModuleInit(): void {
    this.create({ title: 'Ноутбук Pro 16', price: 45000, warrantyMonths: 24, cpu: 'Intel Core i7', ramGb: 16 });
    this.create({ title: 'Смартфон Nova', price: 30000, warrantyMonths: 12, cpu: 'Snapdragon 8 Gen 3', ramGb: 12 });
    this.logger.log('Ініціалізація модуля завершена. Завантажено 2 гаджети.');
  }

  create(dto: CreateGadgetDto): GadgetEntity {
    const gadget: GadgetEntity = {
      id: String(this.nextId++),
      title: dto.title,
      slug: this.slugService.generateSlug(dto.title),
      price: dto.price,
      warrantyMonths: dto.warrantyMonths,
      cpu: dto.cpu,
      ramGb: dto.ramGb,
    };
    this.gadgets.push(gadget);
    return gadget;
  }

  findAll(search?: string, limit?: number): GadgetEntity[] {
    const items = search
      ? this.gadgets.filter((gadget) => gadget.title.toLocaleLowerCase().includes(search.toLocaleLowerCase()))
      : this.gadgets;
    return limit === undefined ? [...items] : items.slice(0, limit);
  }

  findOne(id: string): GadgetEntity {
    const gadget = this.gadgets.find((entry) => entry.id === id);
    if (!gadget) throw new NotFoundException(`Гаджет ${id} не знайдено`);
    return gadget;
  }

  update(id: string, dto: UpdateGadgetDto): GadgetEntity {
    const gadget = this.findOne(id);
    if (dto.title !== undefined) {
      gadget.title = dto.title;
      gadget.slug = this.slugService.generateSlug(dto.title);
    }
    if (dto.price !== undefined) gadget.price = dto.price;
    if (dto.warrantyMonths !== undefined) gadget.warrantyMonths = dto.warrantyMonths;
    if (dto.cpu !== undefined) gadget.cpu = dto.cpu;
    if (dto.ramGb !== undefined) gadget.ramGb = dto.ramGb;
    return gadget;
  }

  remove(id: string): void {
    this.findOne(id);
    this.gadgets.splice(this.gadgets.findIndex((gadget) => gadget.id === id), 1);
  }
}
