import { Injectable, Logger, NotFoundException, OnModuleInit } from '@nestjs/common';
import { SlugService } from '../shared/slug.service';
import { ClothingEntity } from './clothing.entity';
import { CreateClothingDto } from './dto/create-clothing.dto';
import { UpdateClothingDto } from './dto/update-clothing.dto';

@Injectable()
export class ClothesService implements OnModuleInit {
  private readonly logger = new Logger(ClothesService.name);
  private readonly clothes: ClothingEntity[] = [];
  private nextId = 1;

  constructor(private readonly slugService: SlugService) {}

  onModuleInit(): void {
    this.create({ title: 'Куртка зимова', category: 'Одяг', price: 2500 });
    this.create({ title: 'Кросівки Sport', category: 'Взуття', price: 1800 });
    this.logger.log('Ініціалізація модуля завершена. Завантажено початкові тестові дані.');
  }

  create(dto: CreateClothingDto): ClothingEntity {
    const item: ClothingEntity = {
      id: `clothing-${this.nextId++}`,
      title: dto.title,
      slug: this.slugService.generateSlug(dto.title),
      category: dto.category,
      price: dto.price,
    };
    this.clothes.push(item);
    return item;
  }

  findAll(search?: string, limit?: number): ClothingEntity[] {
    const items = search
      ? this.clothes.filter((item) => item.title.toLocaleLowerCase().includes(search.toLocaleLowerCase()))
      : this.clothes;
    return limit === undefined ? [...items] : items.slice(0, limit);
  }

  findOne(id: string): ClothingEntity {
    const item = this.clothes.find((entry) => entry.id === id);
    if (!item) throw new NotFoundException(`Товар ${id} не знайдено`);
    return item;
  }

  update(id: string, dto: UpdateClothingDto): ClothingEntity {
    const item = this.findOne(id);
    if (dto.title !== undefined) {
      item.title = dto.title;
      item.slug = this.slugService.generateSlug(dto.title);
    }
    if (dto.category !== undefined) item.category = dto.category;
    if (dto.price !== undefined) item.price = dto.price;
    return item;
  }

  remove(id: string): void {
    this.findOne(id);
    this.clothes.splice(this.clothes.findIndex((item) => item.id === id), 1);
  }
}
