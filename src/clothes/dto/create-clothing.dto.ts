import { IsNotEmpty, IsNumber, IsString, Min } from 'class-validator';

export class CreateClothingDto {
  @IsString()
  @IsNotEmpty()
  title!: string;

  @IsString()
  @IsNotEmpty()
  category!: string;

  @IsNumber({ maxDecimalPlaces: 2 })
  @Min(0)
  price!: number;
}
